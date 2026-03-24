import struct
import os

filePath = input("Enter file path: ")

def readFile(path_to_file):
    SIGNATURE = b'\x89PNG\r\n\x1a\n'
    with open(path_to_file, 'rb') as file:
        file_beginning = file.read(8)
        return file_beginning == SIGNATURE


def decode(path_to_file):
    with open(path_to_file, 'rb') as file:
        file.read(8) #We already have checked first 8 bits in readFile()

        file.read(4) #chunk length is always 13

        chunk_type = file.read(4)
        if chunk_type != b'IHDR':
            raise ValueError("Error: The first block after signature is not IHDR.")
        
        ihdr_data = file.read(13)
        width, height, bit_depth, color_type, compression, filter_method, interlace = struct.unpack('>IIBBBBB', ihdr_data)

        return {
            "Width (px)": width,
            "Height (px)": height,
            "Bit depth": bit_depth,
            "Color type": color_type,
            "Compression": compression,
            "Filter": filter_method,
            "Interlace": interlace
        }

try:
    if readFile(filePath):
        print("Signature verified. Decoding PNG header...\n")
        png_info = decode(filePath)
        size_in_byte = os.path.getsize(filePath)
        print(f"File size on disk: {size_in_byte} bytes.")
        print("Info found:")
        for key, value in png_info.items():
            print(f"{key}: {value}")
        print("\nOpening image viewer...")
        os.startfile(filePath)
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Error {e}")