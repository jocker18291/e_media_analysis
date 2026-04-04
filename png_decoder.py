import binascii
import struct
import zlib


def is_critical_chunk(chunk_type):
    # Uppercase first type byte means critical, lowercase means ancillary.
    return bool(chunk_type) and (chunk_type[0] & 0x20) == 0


def decode(path_to_file):
    with open(path_to_file, 'rb') as file:
        file.read(8)  # First 8 bytes are the PNG signature.

        while True:
            length_bytes = file.read(4)
            if not length_bytes:
                break
            length = struct.unpack('>I', length_bytes)[0]

            chunk_type = file.read(4)
            chunk_data = file.read(length)
            file.read(4)  # CRC is read to advance the stream.
            block_name = chunk_type.decode('ascii', errors='ignore')

            if is_critical_chunk(chunk_type):
                print(f"\n[+] Critical chunk found: {block_name} (Size: {length} bytes)")

                if chunk_type == b'IHDR':
                    w, h, depth, c_type, comp, filt, interl = struct.unpack('>IIBBBBB', chunk_data)
                    print(f"    Width: {w} px, Height: {h} px")
                    print(f"    Byte Depth: {depth}, Color type: {c_type}")
                    print(f"    Compression: {comp}, Filter: {filt}, Interlace: {interl}")

                elif chunk_type == b'PLTE':
                    color_quantity = length // 3
                    print(f"    Table of pallete consists of: {color_quantity} colors.")

                elif chunk_type == b'IDAT' and length > 0:
                    hex_data = binascii.hexlify(chunk_data[:16]).decode('ascii')
                    print(f"    Content of the file (HEX): {hex_data}...")
                    print("    (The rest was ignored to ensure the readability for the user)")
                
                elif chunk_type == b'IEND':
                    print("    It means the valid end of png file")
                    break
                
            else:
                print(f"\n[~] Ancillary chunk found: {block_name} (Size: {length} bytes)")

                if chunk_type == b'tEXt':
                    parts = chunk_data.split(b'\x00', 1)

                    if len(parts) == 2:
                        keyword = parts[0].decode('latin-1')
                        text_content = parts[1].decode('latin-1')
                        print(f"    Keyword: {keyword}")
                        print(f"    Text: {text_content}")
                    else:
                        print("    [!] Failed to split tEXt chunk.")

                elif chunk_type == b'tIME':
                    if length == 7:
                        year, month, day, hour, minute, second = struct.unpack('>HBBBBB', chunk_data)

                        date_str = f"{year}-{month:02d}-{day:02d}"
                        time_str = f"{hour:02d}:{minute:02d}:{second:02d}"

                        print(f"    Last Modification: {date_str} at {time_str}")
                    else:
                        print("    [!] Invalid tIME chunk. Expected 7 bytes.")
                
                elif chunk_type == b'zTXt':
                    parts = chunk_data.split(b'\x00', 1)

                    if len(parts) == 2:
                        keyword = parts[0].decode('latin-1', errors='ignore')
                        
                        # The first byte of the second part is the compression method
                        compression_method = parts[1][0]
                        # Everything after the first byte is the actual zipped text
                        compressed_data = parts[1][1:]

                        print(f"    [!] Complex Chunk Detected: zTXt (Compressed Text)")
                        print(f"    Keyword: {keyword}")

                        if compression_method == 0:
                            try:
                                decompressed_bytes = zlib.decompress(compressed_data)
                                decompressed_text = decompressed_bytes.decode('latin-1', errors='ignore')
                                
                                # Print only first 50 characters so it doesn't flood the console
                                print(f"    Decompressed Text: {decompressed_text[:50]}...")
                                print(f"    (Compression saved {len(compressed_data)} -> {len(decompressed_bytes)} bytes)")
                            except zlib.error:
                                print("    [!] Failed to decompress zlib data.")
                        else:
                            print(f"    [!] Unknown compression method: {compression_method}")
                    else:
                        print("    [!] Failed to parse zTXt chunk.")