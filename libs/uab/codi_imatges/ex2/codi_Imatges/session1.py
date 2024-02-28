import metrikz
from PIL import Image
import cv2

I = Image.open("image1.png")

print(I.size, I.mode, I.format)

I.save(f"image1.jpg",quality = 1)

source = cv2.imread("image1.png")
target = cv2.imread("image1.jpg")

print (metrikz.mse(source, target))

