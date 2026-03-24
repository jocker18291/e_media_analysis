import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import struct
import os
import binascii

filePath = input("Enter file path: ")

def readFile(path_to_file):
    SIGNATURE = b'\x89PNG\r\n\x1a\n'
    with open(path_to_file, 'rb') as file:
        file_beginning = file.read(8)
        return file_beginning == SIGNATURE


def decode(path_to_file):
    with open(path_to_file, 'rb') as file:
        file.read(8) #We already have checked first 8 bits in readFile()

        while True:
            length_bytes = file.read(4)
            if not length_bytes:
                break
            length = struct.unpack('>I', length_bytes)[0]

            chunk_type = file.read(4)
            chunk_data = file.read(length)

            crc = file.read(4)

            if chunk_type in [b'IHDR', b'PLTE', b'IDAT', b'IEND']:
                block_name = chunk_type.decode('ascii')
                print(f"\n[+] Critical chunk found: {block_name} (Size: {length} bytes)")

                if chunk_type == b'IHDR':
                    w, h, depth, c_type, comp, filt, interl = struct.unpack('>IIBBBBB', chunk_data)
                    print(f"    Width: {w} px, Height: {h} px")
                    print(f"    Byte Depth: {depth}, Color type: {c_type}")
                    print(f"    Compression: {comp}, Filter: {filt}, Interlace: {interl}")
                
                elif chunk_type == b'PLTE':
                    color_quantity = length // 3
                    print(f"    Table of pallete consists of: {color_quantity} colors.")
                
                elif chunk_type == b'IDAT':
                    if length > 0:
                        hex_data = binascii.hexlify(chunk_data[:16]).decode('ascii')
                        print(f"    Content of the file (HEX): {hex_data}...")
                        print(f"    (The rest was ignored to ensure the readability for the user)")
                
                elif chunk_type == b'IEND':
                    print(f"    It means the valid end of png file")
                    break
            else:
                pass


def fourier(path_to_file):
    img = Image.open(path_to_file).convert('L') #Converting image to grayscale
    img_data = np.array(img) #transfering data to array
    
    f_transform = np.fft.fft2(img_data) #fast fourier transform
    f_shift = np.fft.fftshift(f_transform) #we shift the zero frequency to the center

    magnitude_spectrum = np.abs(f_shift) #magnitude spectrum calculation
    magnitude_spectrum_log = np.log1p(magnitude_spectrum) #calculated magnitude we transform to log scale

    #This code tests the fourier transform. If the error equals 0.0000000000 then the transformation went correct
    f_ishift = np.fft.ifftshift(f_shift)
    img_back = np.fft.ifft2(f_ishift)
    img_back_real = np.abs(img_back)
    mean_error = np.mean(np.abs(img_data - img_back_real))
    print(f"\nInverse mean error: {mean_error:.10f}")

    plt.figure(figsize=(12, 6))
    plt.subplot(131)
    plt.imshow(img_data, cmap='gray')
    plt.title('Original Image (Grayscale)')
    plt.axis('off')

    plt.subplot(132)
    plt.imshow(magnitude_spectrum_log, cmap='magma')
    plt.title('Fourier Magnitude Spectrum (Log Scale)')
    plt.axis('off')

    plt.subplot(133)
    plt.imshow(img_back_real, cmap='gray')
    plt.title('Extraction of the Original Image')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

try:
    if readFile(filePath):
        print("Signature verified. Decoding PNG header...\n")
        size_in_byte = os.path.getsize(filePath)
        print(f"File size on disk: {size_in_byte} bytes.")
        decode(filePath)
        print("\nOpening image viewer...")
        os.startfile(filePath)
        print("\nOpening Plots...")
        fourier(filePath)
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Error {e}")