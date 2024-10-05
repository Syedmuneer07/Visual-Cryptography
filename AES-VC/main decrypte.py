import base64
import hashlib
import numpy as np
import cv2
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import os

# Class definition for AESCipher
class AESCipher:
    def __init__(self, data, key):
        self.block_size = 16
        self.data = data
        self.key = hashlib.sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        plain_text = self.pad(self.data)
        iv = get_random_bytes(self.block_size)
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return base64.b64encode(iv + cipher.encrypt(plain_text.encode())).decode()

    def decrypt(self):
        cipher_text = base64.b64decode(self.data.encode())
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        try:
            decrypted = cipher.decrypt(cipher_text[self.block_size:])
            return self.unpad(decrypted).decode('utf-8')
        except Exception as e:
            print(f"Error during decryption: {e}")
            return None

# Get folder path from user
folder_path = input("Enter the folder path containing the files (e.g., 'shares'): ").strip().strip('"')

# Define file paths
cipher_path = os.path.join(folder_path, 'cipher.txt')
P_path = os.path.join(folder_path, 'P.png')
R_path = os.path.join(folder_path, 'R.png')
xy_path = os.path.join(folder_path, 'xy_values.txt')

# Check if all required files exist
if not os.path.isfile(cipher_path) or not os.path.isfile(P_path) or not os.path.isfile(R_path) or not os.path.isfile(xy_path):
    print("One or more required files are missing. Please check the folder path and ensure all required files are present.")
    exit()

# Load cipher text
with open(cipher_path, 'r', encoding='utf-8') as f:
    cipher_base64 = f.read()
cipher = base64.b64decode(cipher_base64).decode('utf-8')

# Load shares
P = cv2.imread(P_path)
R = cv2.imread(R_path)

h, w, _ = P.shape

# Reconstruct the Key
CK = np.ones((h, w, 1), dtype='uint8')

for i in range(h):
    for j in range(w):
        ck = P[i][j][0] ^ R[i][j][0]
        CK[i][j][0] = ck

K1 = []
for i in range(len(CK)):
    count = 0
    for j in range(len(CK[i])):
        if CK[i][j][0] == 0:
            count += 1
    K1.append(chr(count))

K1 = "".join(K1)

# Compute the SHA256 hash of the reconstructed key
SK1 = hashlib.sha256(K1.encode()).hexdigest()
print("The hexadecimal equivalent of SHA256 is : ")
print(SK1)

# Load x and y values from the file
with open(xy_path, 'r') as f:
    x = int(f.readline().strip())
    y = int(f.readline().strip())

# Decrypt cipher text using the reconstructed key
cipher = cipher.split(' ')

txt = []
for each in cipher:
    try:
        ch = ord(each) - x + y
        txt.append(int(ch))
    except:
        print(each)

text = "".join(chr(t) for t in txt)

decrypted_text = AESCipher(text, SK1).decrypt()

if decrypted_text is not None:
    decrypted_text = decrypted_text.encode("utf-8")

    with open(os.path.join(folder_path, "DecryptedImg.png"), "wb") as fh:
        fh.write(base64.decodebytes(decrypted_text))

    print("Decryption complete. Image saved as 'DecryptedImg.png'.")
else:
    print("Decryption failed due to invalid key or corrupted data.")
