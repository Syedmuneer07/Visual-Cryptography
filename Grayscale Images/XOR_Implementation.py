import numpy as np
from PIL import Image
from GrayscaleMetrics import psnr, normxcorr2D
import os

def encrypt(input_image, share_size):
    image = np.asarray(input_image)
    (row, column) = image.shape
    shares = np.random.randint(0, 256, size=(row, column, share_size))
    shares[:, :, -1] = image.copy()
    for i in range(share_size - 1):
        shares[:, :, -1] = shares[:, :, -1] ^ shares[:, :, i]

    return shares, image

def decrypt(shares):
    (row, column, share_size) = shares.shape
    shares_image = shares.copy()
    for i in range(share_size - 1):
        shares_image[:, :, -1] = shares_image[:, :, -1] ^ shares_image[:, :, i]

    final_output = shares_image[:, :, share_size - 1]
    output_image = Image.fromarray(final_output.astype(np.uint8))
    return output_image, final_output

if __name__ == "__main__":
    print("Enter the path of the input image file:\n")

    image_path = input("Image path: ").strip().strip('\"\'')  # Remove surrounding quotes if present

    try:
        input_image = Image.open(image_path).convert('L')
    except FileNotFoundError:
        print("Input file not found!")
        exit(0)
    except IOError:
        print("Invalid image file!")
        exit(0)

    print("Image uploaded successfully!")
    print("Input image size (in pixels) : ", input_image.size)

    try:
        share_size = int(input("Input the number of shares images you want to create for encrypting (min is 2, max is 8) : "))
        if share_size < 2 or share_size > 8:
            raise ValueError
    except ValueError:
        print("Input is not a valid integer!")
        exit(0)

    print("Number of shares image = ", share_size)

    # Create output directory if it doesn't exist
    output_dir = 'output grayscale'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    shares, input_matrix = encrypt(input_image, share_size)

    for ind in range(share_size):
        image = Image.fromarray(shares[:, :, ind].astype(np.uint8))
        name = os.path.join(output_dir, f"XOR_Share_{ind + 1}.png")
        image.save(name)

    output_image, output_matrix = decrypt(shares)

    output_image.save(os.path.join(output_dir, 'Output_XOR.png'))
    print("Image is saved 'Output_XOR.png' ...")

    print("Evaluation metrics : ")    
    print(f"PSNR value is {psnr(input_matrix, output_matrix)} dB")
    print(f"Mean NCORR value is {normxcorr2D(input_matrix, output_matrix)}")
