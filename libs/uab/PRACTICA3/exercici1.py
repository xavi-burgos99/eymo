from metrikz import *
import numpy as np
import time
from PIL import Image
import numpy as np


def calcular_sad(bloque1, bloque2):
    """Calcula la Suma de Diferencias Absolutas (SAD) entre dos bloques."""
    return np.sum(np.abs(bloque1 - bloque2))


def block_matching(frame_actual, frame_anterior, tamaño_bloque=8, restriccion=False, tamaño_ventana=24):
    assert (tamaño_ventana - tamaño_bloque > 0)
    assert (tamaño_ventana % 2 == 0)
    alto, ancho = frame_actual.shape

    # Arrays to store data
    vectores_movimiento = []
    errores_prediccion = []

    mse_total = 0

    s = time.time()

    for y in range(0, alto, tamaño_bloque):
        for x in range(0, ancho, tamaño_bloque):
            bloque_actual = frame_actual[y:y + tamaño_bloque, x:x + tamaño_bloque]
            sad_min = np.inf
            mejor_movimiento = (0, 0)
            mejor_bloque = None

            # Determinar los límites de la región de búsqueda
            y_min = max(0, y - (tamaño_ventana // 2) - tamaño_bloque // 2) if restriccion else 0
            y_max = min(alto, y + (tamaño_ventana // 2) + tamaño_bloque // 2) if restriccion else alto
            x_min = max(0, x - (tamaño_ventana // 2) - tamaño_bloque // 2) if restriccion else 0
            x_max = min(ancho, x + (tamaño_ventana // 2) + tamaño_bloque // 2) if restriccion else ancho

            step = 1 if restriccion else tamaño_bloque
            for y_ref in range(y_min, y_max - tamaño_bloque + 1, step):
                for x_ref in range(x_min, x_max - tamaño_bloque + 1, step):
                    bloque_ref = frame_anterior[y_ref:y_ref + tamaño_bloque, x_ref:x_ref + tamaño_bloque]
                    sad_actual = calcular_sad(bloque_actual, bloque_ref)

                    if sad_actual < sad_min:
                        sad_min = sad_actual
                        mejor_movimiento = (x_ref - x, y_ref - y)
                        mejor_bloque = bloque_ref

            vectores_movimiento.append(mejor_movimiento)
            errores_prediccion.append(sad_min)
            mse_total += mse(bloque_actual, mejor_bloque)

    mse_promedio = mse_total / len(vectores_movimiento)

    e = time.time()
    time_bm = e - s
    return vectores_movimiento, errores_prediccion, mse_promedio, time_bm


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
    vectores_movimiento, errores_prediccion, mse_promedio, time_bm = block_matching(
        frame_actual_np, frame_anterior_np, tamaño_bloque, restriccion=True
    )

    # Imprimir los resultados
    print("Vectores de movimiento:", vectores_movimiento)
    print("Errores de predicción:", errores_prediccion)

    print("MSE promedio:", mse_promedio)
    print("Timepo de ejecución:", time_bm)
