import metrikz
from scipy import misc
from PIL import Image

I = Image.open("image1.png")

print I.size, I.mode, I.format

I.save("image1.jpg",quality = 1)

source = misc.imread("image1.png")
target = misc.imread("image1.jpg")

print metrikz.mse(source, target)

