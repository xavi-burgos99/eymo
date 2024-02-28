import metrikz
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt

# Inicialitzar la figura fora del bucle
plt.figure(figsize=(12, 8))

# Bucle per processar les imatges del 1 al 8
for i in range(1, 9):
    image_path = os.path.join("", f"image{i}.png")

    mse_values = []  # Llista per emmagatzemar els valors MSE
    quality_values = list(range(0, 101, 10))  # Valors de qualitat de 0 a 100 amb increments de 10

    # Comprovar si l'imatge existeix
    if os.path.exists(image_path):
        # Obrir l'imatge original
        I = Image.open(image_path)

        # Comprimir i guardar l'imatge en format JPEG amb diferents qualitats
        for quality in quality_values:
            if quality == 0:  # La qualitat 0 no és vàlida, es fa servir 1 com a mínim
                quality = 1
            compressed_image_path = os.path.join("compressed/", f"image{i}_quality{quality}.jpg")
            I.save(compressed_image_path, quality=quality)

            # Llegir l'imatge original i la comprimida per calcular l'MSE
            source = cv2.imread(image_path)
            target = cv2.imread(compressed_image_path)
            mse_value = metrikz.mse(source, target)
            mse_values.append(mse_value)

        # Afegir els valors MSE al gràfic
        plt.plot(quality_values, mse_values, marker='o', linestyle='-', label=f'Image {i}')

    else:
        print(f"Image {i} not found.")

# Configurar el gràfic
plt.title('MSE vs JPEG Quality for All Images')
plt.xlabel('JPEG Quality')
plt.ylabel('MSE')
plt.legend()
plt.grid(True)

# Desar la figura
plt.savefig('figure1.png', format='png', dpi=300)

# Mostrar la figura (opcional)
plt.show()
