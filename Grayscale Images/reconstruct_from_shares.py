import numpy as np
from PIL import Image
import os

def decrypt(shares):
    (row, column, share_size) = shares.shape
    shares_image = shares.copy()
    for i in range(share_size - 1):
        shares_image[:, :, -1] = shares_image[:, :, -1] ^ shares_image[:, :, i]

    final_output = shares_image[:, :, share_size - 1]
    output_image = Image.fromarray(final_output.astype(np.uint8))
    return output_image, final_output

def reconstruct_image(shares_folder):
    # Read all share images from the folder
    share_files = sorted([f for f in os.listdir(shares_folder) if f.startswith('XOR_Share_') and f.endswith('.png')])
    
    if not share_files:
        print("No share images found in the specified folder!")
        return
    
    # Initialize variables for size
    row, column = None, None
    share_size = len(share_files)
    
    # Initialize array for shares
    shares = None

    # Load each share into the shares array
    for ind, file_name in enumerate(share_files):
        share_image = Image.open(os.path.join(shares_folder, file_name))
        img_array = np.asarray(share_image)

        if row is None and column is None:
            # Determine size from the first share
            row, column = img_array.shape
            shares = np.zeros((row, column, share_size), dtype=np.uint8)
        elif img_array.shape != (row, column):
            print(f"Error: Share image '{file_name}' has different dimensions.")
            return

        shares[:, :, ind] = img_array

    # Reconstruct the original image
    reconstructed_image, _ = decrypt(shares)

    # Save the reconstructed image
    reconstructed_image.save(os.path.join(shares_folder, 'Reconstructed_Image.png'))
    print("Reconstructed image saved as 'Reconstructed_Image.png' ...")

if __name__ == "__main__":
    print("Enter the path of the folder containing share images:\n")
    shares_folder = input("Folder path: ").strip().strip('\"\'')  # Remove surrounding quotes if present

    if not os.path.exists(shares_folder):
        print("Folder does not exist!")
        exit(0)

    reconstruct_image(shares_folder)

