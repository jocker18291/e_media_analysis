import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def fourier(path_to_file):
    img = Image.open(path_to_file).convert('L')  # Convert image to grayscale.
    img_data = np.array(img)

    f_transform = np.fft.fft2(img_data)
    f_shift = np.fft.fftshift(f_transform)

    magnitude_spectrum = np.abs(f_shift)
    magnitude_spectrum_log = np.log1p(magnitude_spectrum)

    # Validate inverse transform quality.
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
