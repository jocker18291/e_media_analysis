import struct


CRITICAL_CHUNKS = [b'IHDR', b'PLTE', b'IDAT', b'IEND']


def anonymize(path_to_file, output_path):
    """
    Keeps only critical chunks (removes metadata).
    """
    with open(path_to_file, 'rb') as file_in, open(output_path, 'wb') as file_out:
        signature = file_in.read(8)
        file_out.write(signature)

        while True:
            length_bytes = file_in.read(4)
            if not length_bytes:
                break

            length = struct.unpack('>I', length_bytes)[0]

            chunk_type = file_in.read(4)
            chunk_data = file_in.read(length)
            crc = file_in.read(4)

            if chunk_type in CRITICAL_CHUNKS:
                file_out.write(length_bytes)
                file_out.write(chunk_type)
                file_out.write(chunk_data)
                file_out.write(crc)
            else:
                print(f"\n[-] Removed chunk: {chunk_type.decode('ascii', errors='ignore')}")
