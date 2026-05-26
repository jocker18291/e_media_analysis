import struct
import binascii


# PNG signature constant
PNG_SIGNATURE = b'\x89PNG\r\n\x1a\n'

# Chunks essential for image rendering
ESSENTIAL_CHUNKS = {b'IHDR', b'PLTE', b'IDAT', b'IEND'}

# Ancillary chunks containing metadata/offsets that should be removed
METADATA_CHUNKS = {
    b'tEXt', b'zTXt', b'iTXt',  # Text data
    b'tIME', b'pHYs',            # Timing and physical dimensions
    b'gAMA', b'cHRM', b'sRGB',   # Color space information
    b'iCCP', b'sPLT',            # Color profiles
    b'bKGD', b'tRNS',            # Background, transparency hints
    b'gIFg', b'gIFx', b'gIFt',   # GIF extension chunks
    b'hISt',                      # Histogram
    b'eXIf', b'eXIf'             # EXIF data
}


def _validate_crc(chunk_type, chunk_data, crc_bytes):
    """
    Validate CRC32 checksum for a chunk.
    Returns True if CRC is valid, False otherwise.
    """
    try:
        expected_crc = struct.unpack('>I', crc_bytes)[0]
        calculated_crc = binascii.crc32(chunk_type + chunk_data) & 0xffffffff
        return expected_crc == calculated_crc
    except Exception:
        return False


def _read_chunk(file_obj):
    """
    Read a single PNG chunk from file.
    Returns (length_bytes, chunk_type, chunk_data, crc_bytes) or None if EOF.
    """
    length_bytes = file_obj.read(4)
    if not length_bytes:
        return None

    length = struct.unpack('>I', length_bytes)[0]
    chunk_type = file_obj.read(4)
    chunk_data = file_obj.read(length)
    crc_bytes = file_obj.read(4)

    return (length_bytes, chunk_type, chunk_data, crc_bytes)


def anonymize(path_to_file, output_path):
    """
    Keeps only critical chunks (removes metadata).
    
    Preserves:
    - PNG signature
    - IHDR (image header with dimensions)
    - PLTE (palette, if present)
    - IDAT (image data)
    - IEND (end marker)
    
    Removes:
    - All ancillary chunks (text, timing, color profiles, etc.)
    - Chunks containing file structure metadata
    """
    try:
        with open(path_to_file, 'rb') as file_in, open(output_path, 'wb') as file_out:
            # Validate and write PNG signature
            signature = file_in.read(8)
            if signature != PNG_SIGNATURE:
                print(f"[-] Error: Invalid PNG file signature in '{path_to_file}'")
                return False

            file_out.write(signature)

            removed_chunks = {}
            total_bytes_removed = 0
            output_offset = 8  # Track output file offset
            chunk_count = 0

            while True:
                chunk_info = _read_chunk(file_in)
                if chunk_info is None:
                    break

                length_bytes, chunk_type, chunk_data, crc_bytes = chunk_info
                chunk_length = struct.unpack('>I', length_bytes)[0]
                chunk_name = chunk_type.decode('ascii', errors='ignore')
                chunk_size = 4 + 4 + chunk_length + 4  # length + type + data + CRC

                # Validate CRC for data integrity check
                crc_valid = _validate_crc(chunk_type, chunk_data, crc_bytes)
                crc_status = "✓" if crc_valid else "✗"

                # Decision logic: keep essential chunks, remove metadata
                if chunk_type in ESSENTIAL_CHUNKS:
                    file_out.write(length_bytes)
                    file_out.write(chunk_type)
                    file_out.write(chunk_data)
                    file_out.write(crc_bytes)
                    output_offset += chunk_size
                    chunk_count += 1

                else:
                    # Chunk is ancillary/metadata - remove it
                    total_bytes_removed += chunk_size
                    removed_chunks[chunk_name] = removed_chunks.get(chunk_name, 0) + 1
                    print(f"  [-] Removed: {chunk_name:8s} ({chunk_length:6d} bytes) [CRC {crc_status}]")

                # Stop processing after IEND chunk
                if chunk_type == b'IEND':
                    break

            # Summary output
            print(f"\n[+] Anonymization complete")
            print(f"    Output file: {output_path}")
            print(f"    Chunks retained: {chunk_count}")
            print(f"    Total bytes removed: {total_bytes_removed}")

            if removed_chunks:
                print(f"    Removed chunk types:")
                for chunk_name, count in sorted(removed_chunks.items()):
                    print(f"      • {chunk_name}: {count}")

            return True

    except FileNotFoundError:
        print(f"[-] Error: File not found: '{path_to_file}'")
        return False
    except Exception as e:
        print(f"[-] Error during anonymization: {e}")
        return False
