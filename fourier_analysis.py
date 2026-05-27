import matplotlib.pyplot as plt
import numpy as np
from PIL import Image


def fourier(path_to_file):
    img = Image.open(path_to_file).convert('L')  # Convert image to grayscale. 'L' stands for 'Luminance'
    # It is calculated from the formula L = R * 0.299 + G * 0.587 + B * 0.114
    # The method uses C language and coefficients are put due to different color seeing of human eye
    img_data = np.array(img)

    f_transform = np.fft.fft2(img_data) #It transforms the image using Cooley-Tukey algorithm (Divide and Conquer)
    # It uses O(NlogN) time complexity
    # Returns the sum of polynomials described by Euler's formula exp(ix) = cosx + isinx
    f_shift = np.fft.fftshift(f_transform) # It just shuffles four different parts of the photo in fourier transform

    magnitude_spectrum = np.abs(f_shift) # It calculates the absolute value of the complex number z = a + bi
    # It uses processor optimization (SIMD/AVX) so it can calculate a dozen of values simultaneously
    # This method uses C language
    magnitude_spectrum_log = np.log1p(magnitude_spectrum) # optimization of numeric stability
    # It calculates the Taylor series for super small numbers, i.e. 10e-16

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
