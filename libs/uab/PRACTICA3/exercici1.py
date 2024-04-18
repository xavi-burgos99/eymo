from metrikz import *

from PIL import Image
import numpy as np
import sessio3


if __name__ == '__main__':
    # Cargar las imágenes y convertirlas a escala de grises
    frame_anterior = Image.open('frame2_1.png').convert('L')
    frame_actual = Image.open('frame2_2.png').convert('L')

    # Convertir las imágenes a arrays de NumPy
    frame_anterior_np = np.array(frame_anterior)
    frame_actual_np = np.array(frame_actual)

    # Imprimir las dimensiones para confirmar
    print("Frame Anterior:", frame_anterior_np.shape)
    print("Frame Actual:", frame_actual_np.shape)

    # Definir el tamaño del bloque
    tamaño_bloque = 8

    # Aplicar el algoritmo de Block Matching
    vectores_movimiento, errores_prediccion, mse_promedio, time_bm, _ = sessio3.block_matching(
        frame_actual_np, frame_anterior_np, tamaño_bloque, restriccion=False
    )

    # Imprimir los resultados
    #print("Vectores de movimiento:", vectores_movimiento)
    #print("Errores de predicción:", errores_prediccion)

    print("MSE promedio:", round(mse_promedio, 2))
    print("Tiempo de ejecución:", round(time_bm, 2), " s")
