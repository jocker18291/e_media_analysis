import os
from PIL import Image
import zipfile

def analyze_weight(file_path):
    img_rgb = Image.open(file_path).convert('RGB')
    img_rgb.save("result_dedicated.png", optimize=True)

    with open("raw_data.bin", "wb") as f:
        f.write(img_rgb.tobytes())
    
    with zipfile.ZipFile("result_general.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write("raw_data.bin")
    
    size_png = os.path.getsize("result_dedicated.png")
    size_zip = os.path.getsize("result_general.zip")

    print(f"PNG (Dedicated): {size_png} bytes")
    print(f"RAW + ZIP (General): {size_zip} bytes")