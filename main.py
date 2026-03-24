import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
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

def fourier(path_to_file):
    img = Image.open(path_to_file).convert('L') #Converting image to grayscale
    img_data = np.array(img) #transfering data to array
    
    f_transform = np.fft.fft2(img_data) #fast fourier transform
    f_shift = np.fft.fftshift(f_transform) #we shift the zero frequency to the center

    magnitude_spectrum = np.abs(f_shift) #magnitude spectrum calculation
    magnitude_spectrum_log = np.log1p(magnitude_spectrum) #calculated magnitude we transform to log scale

    plt.figure(figsize=(12, 6))
    plt.subplot(121)
    plt.imshow(img_data, cmap='gray')
    plt.title('Original Image (Grayscale)')
    plt.axis('off')

    plt.subplot(122)
    plt.imshow(magnitude_spectrum_log, cmap='magma')
    plt.title('Fourier Magnitude Spectrum (Log Scale)')
    plt.axis('off')

    plt.tight_layout()
    plt.show()

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
        print("\nOpening Plots...")
        fourier(filePath)
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Error {e}")