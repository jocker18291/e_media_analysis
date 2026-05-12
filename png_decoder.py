import binascii
import struct


def decode(path_to_file):
    with open(path_to_file, 'rb') as file:
        file.read(8)  # First 8 bytes are the PNG signature.
        color_type = None
        while True:
            length_bytes = file.read(4)
            if not length_bytes:
                break
            length = struct.unpack('>I', length_bytes)[0]

            chunk_type = file.read(4)
            chunk_data = file.read(length)
            file.read(4)  # CRC is read to advance the stream.

            if chunk_type in [b'IHDR', b'PLTE', b'IDAT', b'IEND']:
                block_name = chunk_type.decode('ascii')
                print(f"\n[+] Critical chunk found: {block_name} (Size: {length} bytes)")

                if chunk_type == b'IHDR':
                    w, h, depth, c_type, comp, filt, interl = struct.unpack('>IIBBBBB', chunk_data)
                    print(f"    Width: {w} px, Height: {h} px")
                    print(f"    Byte Depth: {depth}, Color type: {c_type}")
                    print(f"    Compression: {comp}, Filter: {filt}, Interlace: {interl}")
                    color_type = c_type

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
            
            elif chunk_type in [b'tRNS', b'gAMA', b'cHRM']:
                block_name = chunk_type.decode('ascii')
                print(f"\n[+] Ancillary chunk found: {block_name} (Size: {length} bytes)")

                if chunk_type == b'tRNS':
                    if color_type == 1:
                        print(f"   Transparency for indexed-color: {length} bytes")
                    elif color_type == 2:
                        print(f"   Transparency for true-color: {length} bytes")
                    elif color_type == 3:
                        print(f"   Transparency for grayscale: {length} bytes")
                
                elif chunk_type == b'gAMA':
                    gamma_value = struct.unpack('>I', chunk_data)[0] / 100000
                    print(f"   Gamma value: {gamma_value}")
                
                elif chunk_type == b'cHRM':
                    white_x, white_y, red_x, red_y, green_x, green_y, blue_x, blue_y = struct.unpack('>IIIIIIII', chunk_data)
                    print(f"   Chromaticity: White({white_x}, {white_y}), Red({red_x}, {red_y}), Green({green_x}, {green_y}), Blue({blue_x}, {blue_y})")
