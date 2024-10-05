import base64
from PIL import Image
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import os

# Ensure shares directory exists

if not os.path.exists('shares'):
    os.makedirs('shares')

# Get image path from user
image_path = input("Enter the path to the image file (e.g., 'path_to_your_image.jpg'): ").strip().strip('"')
# Reading image and encoding it
with open(image_path, "rb") as img_file:
    BI = base64.b64encode(img_file.read()).decode("utf-8")

# Key and SHA256
K = "Hello, World. ThisIsMyKey."
SK = hashlib.sha256(K.encode()).hexdigest()
print("The hexadecimal equivalent of SHA256 is : ")
print(SK)

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

# Encrypting image using AES-256
c = AESCipher(BI, SK).encrypt()

# Additional Encryption
w = 255
h = len(K)
C = np.ones((h, w, 1), dtype='uint8')

for i in range(h):
    j = ord(K[i])
    for k in range(w):
        if k < j:
            C[i][k][0] = 0
        else:
            break

R = np.ones((h, w, 3), dtype='uint8')
P = np.ones((h, w, 3), dtype='uint8')

for i in range(h):
    for j in range(w):
        r = np.random.normal(0, 1, 1)[0]  # Extracting single element from array
        R[i][j][0] = r

for i in range(h):
    for j in range(w):
        p = R[i][j][0] ^ C[i][j][0]
        P[i][j][0] = p

plt.imshow(P)
plt.show()

plt.imshow(R)
plt.show()

cv2.imwrite('shares/R.png', R)
cv2.imwrite('shares/P.png', P)

# Encrypt CipherText further
xdf = pd.DataFrame(columns=['1', '2'])
a = []
b = []
for i in P:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k % 2 == 0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1
    a.append(sum(n1))
    b.append(sum(n2))
xdf['1'] = a
xdf['2'] = b

ydf = pd.DataFrame(columns=['1', '2'])
a = []
b = []
for i in R:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k % 2 == 0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1
    a.append(sum(n1))
    b.append(sum(n2))
ydf['1'] = a
ydf['2'] = b

LRmodel = LinearRegression()
LRmodel.fit(xdf, ydf)

zdf = pd.DataFrame(columns=['1', '2'])
a = []
b = []
for i in C:
    k = 0
    n1 = []
    n2 = []
    for j in i:
        if k % 2 == 0:
            n1.append(np.sum(j))
        else:
            n2.append(np.sum(j))
        k += 1
    a.append(sum(n1))
    b.append(sum(n2))
zdf['1'] = a
zdf['2'] = b

predict = LRmodel.predict(pd.DataFrame([[sum(zdf['1']), sum(zdf['2'])]], columns=['1', '2']))

x = round(predict[0][0]) % 26
y = round(predict[0][1]) % 26

# Save x and y values to a file
with open('shares/xy_values.txt', 'w') as f:
    f.write(f"{x}\n{y}")

txt = []
for each in c:
    ch = ord(each) + x - y
    txt.append(int(ch))

text = "".join(chr(t) + " " for t in txt)

file_path = os.path.join('shares', 'cipher.txt')
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(base64.b64encode(text.encode()).decode('utf-8'))

print("Encryption complete. Cipher text saved to 'shares/cipher.txt'.")
print("Shares saved as 'shares/R.png' and 'shares/P.png'.")
print("x and y values saved to 'shares/xy_values.txt'.")
