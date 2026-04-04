import os
from fourier_analysis import fourier
from png_anonymizer import anonymize
from png_decoder import decode
from png_signature import readFile

filePath = input("Enter file path: ")

try:
    if readFile(filePath):
        print("Signature verified. Decoding PNG header...\n")
        size_in_byte = os.path.getsize(filePath)
        print(f"File size on disk: {size_in_byte} bytes.")
        decode(filePath)
        anon_path = filePath.replace(".png", "_anon.png")
        anonymize(filePath, anon_path)
        print("\nOpening image viewer...")
        os.startfile(filePath)
        print("\nOpening Plots...")
        fourier(filePath)
except FileNotFoundError:
    print("File not found.")
except Exception as e:
    print(f"Error {e}")