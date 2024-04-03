import metrikz
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt

# Inicialitzar llistes per emmagatzemar les dades per a tots els gràfics
all_mse_values = []
all_compression_ratios = []
quality_values = list(range(0, 101, 10))  # Valors de qualitat de 1 a 100 amb increments de 10

# Bucle per processar les imatges del 1 al 8
for i in range(1, 9):
    image_path = os.path.join("", f"image{i}.png")

    mse_values = []  # Llista per emmagatzemar els valors MSE
    compression_ratios = []  # Llista per emmagatzemar les relacions de compressió

    # Comprovar si l'imatge existeix
    if os.path.exists(image_path):
        # Obrir l'imatge original i obtenir la mida de l'arxiu original
        I = Image.open(image_path)
        original_size = os.path.getsize(image_path)

        # Comprimir i guardar l'imatge en format JPEG amb diferents qualitats
        for quality in quality_values:
            compressed_image_path = os.path.join("compressed/", f"image{i}_quality{quality}.jpg")
            I.save(compressed_image_path, quality=quality)

            # Llegir l'imatge original i la comprimida per calcular l'MSE
            source = cv2.imread(image_path)
            target = cv2.imread(compressed_image_path)
            mse_value = metrikz.mse(source, target)
            mse_values.append(mse_value)

            # Obtenir la mida de l'arxiu comprimit i calcular la relació de compressió
            compressed_size = os.path.getsize(compressed_image_path)
            compression_ratio = original_size / compressed_size if compressed_size != 0 else 0
            compression_ratios.append(compression_ratio)

        # Emmagatzemar els valors MSE i de relació de compressió per a cada imatge
        all_mse_values.append(mse_values)
        all_compression_ratios.append(compression_ratios)

    else:
        print(f"Image {i} not found.")

# Generar "Figura 1": MSE vs JPEG Quality
plt.figure(figsize=(12, 8))
for i, mse_values in enumerate(all_mse_values, start=1):
    plt.plot(quality_values, mse_values, marker='o', linestyle='-', label=f'Image {i}')
plt.title('MSE vs JPEG Quality for All Images')
plt.xlabel('JPEG Quality')
plt.ylabel('MSE')
plt.legend()
plt.grid(True)
plt.savefig('figure1.png', format='png', dpi=300)
plt.show()

# Generar "Figura 2": Compression Ratio vs JPEG Quality
plt.figure(figsize=(12, 8))
for i, compression_ratios in enumerate(all_compression_ratios, start=1):
    plt.plot(quality_values, compression_ratios, marker='o', linestyle='-', label=f'Image {i}')
plt.title('Compression Ratio vs JPEG Quality for All Images')
plt.xlabel('JPEG Quality')
plt.ylabel('Compression Ratio')
plt.legend()
plt.grid(True)
plt.savefig('figure2.png', format='png', dpi=300)
plt.show()