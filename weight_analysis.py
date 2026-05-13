import os
from PIL import Image
import zipfile
import matplotlib.pyplot as plt

def analyze_weight(dir_path):
    results = {"name": [], "png": [], "zip": []}

    for file in os.listdir(dir_path):
        if file.endswith(".png"):
            path = os.path.join(dir_path, file)
            img = Image.open(path).convert("RGB")

            png_size = os.path.getsize(path)

            raw_path = "temp.bin"
            zip_path = "temp.zip"
            with open(raw_path, "wb") as f:
                f.write(img.tobytes())
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
                z.write(raw_path)
            zip_size = os.path.getsize(zip_path)

            results["name"].append(file)
            results["png"].append(png_size / 1024)
            results["zip"].append(zip_size / 1024)

            isGreater = png_size > zip_size

            print(f"Analyzed {file}: PNG size = {png_size} bytes, ZIP size = {zip_size} bytes. {'PNG is larger' if isGreater else 'ZIP is larger'}.")
    
    os.remove("temp.bin")
    os.remove("temp.zip")
    
    return results

