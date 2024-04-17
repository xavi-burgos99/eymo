import cv2
from scipy.fftpack import dct, idct
from PIL import Image, ImageDraw
import numpy as np
import metrikz
import time
import matplotlib.pyplot as plt

quantization_matrix = [[16.0, 11.0, 10.0, 16.0, 24.0, 40.0, 51.0, 61.0],
                       [12.0, 12.0, 14.0, 19.0, 26.0, 58.0, 60.0, 55.0],
                       [14.0, 13.0, 16.0, 24.0, 40.0, 57.0, 69.0, 56.0],
                       [14.0, 17.0, 22.0, 29.0, 51.0, 87.0, 80.0, 62.0],
                       [18.0, 22.0, 37.0, 56.0, 68.0, 109., 103., 77.0],
                       [24.0, 35.0, 55.0, 64.0, 81.0, 104., 113., 92.0],
                       [49.0, 64.0, 78.0, 87.0, 103., 121., 120., 101.],
                       [72.0, 92.0, 95.0, 98.0, 112., 100., 103., 99.0]]


def dct2(block: np.ndarray) -> np.ndarray:
    """Compute 2D Cosine Transform of Image
    Args:
        block (np.ndarray): An image block
    Returns:
        np.ndarray: 2D DCT of the image block
    """
    return dct(dct(block, axis=0, norm='ortho'), axis=1, norm='ortho');


def idct2(block: np.ndarray) -> np.ndarray:
    """Compute 2D Inverse Cosine Transform of Image
    Args:
        block (np.ndarray): An image block
    Returns:
        np.ndarray: 2D IDCT of the image block
    """
    return idct(idct(block, axis=1, norm='ortho'), axis=0, norm='ortho');


def quantization_process(block: np.ndarray) -> np.ndarray:
    """Quantization of the DCT coefficients
    Args:
        block (np.ndarray): An image block
    Returns:
        np.ndarray: Quantized image block
    """
    qm = np.zeros((8, 8))
    for i in range(int(len(block))):
        for j in range(int(len(block))):
            qm[i][j] = np.round(float(block[i][j]) / quantization_matrix[i][j])
    return qm


def inv_quantization_process(block, quantization_matrix):
    """ Realiza la cuantización inversa de los coeficientes DCT """
    return block * quantization_matrix


def func_quantized(block):
    """Quantization of the DCT coefficients
    Args:
        block (np.ndarray): An image block
    Returns:
        np.ndarray: Quantized image block
    """
    qm = np.zeros((8, 8), dtype=int)
    qm[:, :] = quantization_process(dct2(block[:, :]))
    return qm


def block_matching(frame_actual, frame_anterior, tamaño_bloque=8, restriccion=False, tamaño_ventana=24):
    assert (tamaño_ventana - tamaño_bloque > 0)
    assert (tamaño_ventana % 2 == 0)
    alto, ancho = frame_actual.shape

    # Arrays to store data
    vectores_movimiento = []
    errores_prediccion = []
    actual_position = []

    mse_total = 0

    s = time.time()

    for y in range(0, alto, tamaño_bloque):
        for x in range(0, ancho, tamaño_bloque):
            bloque_actual = frame_actual[y:y + tamaño_bloque, x:x + tamaño_bloque]
            bloque_actual_quant = func_quantized(bloque_actual)

            sad_min = np.inf
            mejor_movimiento = (0, 0)
            mejor_bloque = None

            # Agrega posicion actual al array de posiciones
            actual_position.append((x, y))

            # Determinar los límites de la región de búsqueda
            y_min = max(0, y - (tamaño_ventana // 2) - tamaño_bloque // 2) if restriccion else 0
            y_max = min(alto, y + (tamaño_ventana // 2) + tamaño_bloque // 2) if restriccion else alto
            x_min = max(0, x - (tamaño_ventana // 2) - tamaño_bloque // 2) if restriccion else 0
            x_max = min(ancho, x + (tamaño_ventana // 2) + tamaño_bloque // 2) if restriccion else ancho

            step = 1 if restriccion else tamaño_bloque
            for y_ref in range(y_min, y_max - tamaño_bloque + 1, step):
                for x_ref in range(x_min, x_max - tamaño_bloque + 1, step):
                    bloque_ref = frame_anterior[y_ref:y_ref + tamaño_bloque, x_ref:x_ref + tamaño_bloque]
                    # sad_actual = mse(bloque_actual, bloque_ref)

                    sad_actual = metrikz.mse(bloque_actual, bloque_ref)
                    if sad_actual < sad_min:
                        sad_min = sad_actual
                        mejor_movimiento = (x_ref - x, y_ref - y)
                        mejor_bloque = bloque_ref

            vectores_movimiento.append(mejor_movimiento)
            errores_prediccion.append(np.abs(bloque_actual_quant - func_quantized(mejor_bloque)))
            mse_total += sad_min

    mse_promedio = mse_total / len(vectores_movimiento)

    e = time.time()
    time_bm = e - s
    return vectores_movimiento, errores_prediccion, mse_promedio, time_bm, actual_position


def func_motion_compensation(actual_position: list, motion_vector: list, errors_prediction: list,
                             frame: np.ndarray) -> tuple:
    """Motion compensation algorithm
    Args:
        actual_position (list): List of actual positions
        motion_vector (list): List of motion vectors
        errors_predicio (list): List of quantized errors
        frame (np.ndarray): The reference frame
    Returns:
        tuple: Tuple with the compensated frame and the frame with the errors
    """
    tamaño_bloque = 8
    frame3 = np.zeros(frame.shape, dtype=np.int16)
    frame4 = np.zeros(frame.shape, dtype=np.int16)

    # Per a cada bloc (BL) de I1, copieu la regió corresponent (mirant els vectors de
    # moviment) a la posició de BL a la imatge I3.
    for (x, y), (dx, dy) in zip(actual_position, motion_vector):
        new_x = x + dx
        new_y = y + dy
        frame3[y:y + tamaño_bloque, x:x + tamaño_bloque] = frame[new_y:new_y + tamaño_bloque,
                                                           new_x:new_x + tamaño_bloque]

    # Convert the NumPy array to a PIL Image object
    image = Image.fromarray(frame3.astype(np.uint8), 'L')  # 'L' mode is for grayscale images
    image.show()

    frame4 = np.copy(frame3)
    for i, (x, y) in enumerate(actual_position):
        # Extraer el bloque de errores de predicción
        error_block = errors_prediction[i]

        # Descomprimir el error: cuantización inversa, IDCT e redondeo
        error_block = inv_quantization_process(error_block, quantization_matrix)
        error_block = idct2(error_block)
        error_block = np.round(error_block)
        error_block = error_block.astype(dtype=np.int8)

        # Sumar el error descomprimido al bloque correspondiente en I4
        frame4[y:y + tamaño_bloque, x:x + tamaño_bloque] += error_block.astype(dtype=np.int8)

    # Convert the NumPy array to a PIL Image object
    image = Image.fromarray(frame4.astype(np.uint8), 'L')  # 'L' mode is for grayscale images
    image.show()

    return frame3, frame4


def main():
    I1 = Image.open("frame0_1.png")  # Old frame
    I2 = Image.open("frame0_2.png")  # New frame

    # I1.show()
    img1 = I1.convert('L')
    img1.save('frame1_gray.png')
    img2 = I2.convert('L')
    img2.save('frame2_gray.png')
    # img1.show()

    frame1 = cv2.imread("frame1_gray.png")
    frame2 = cv2.imread("frame2_gray.png")
    cv2.imshow('image', frame1)
    frame1 = frame1[:, :, 0]
    frame2 = frame2[:, :, 0]

    print("Dimensions de la imatge: ")
    print(frame1.shape)
    dim = frame1.shape

    #  Final vectors
    actual_position = []
    motion_vector = []
    errors_prediction = []

    # Block generator matrix
    bl = np.zeros((8, 8))

    #
    # GERENAR AQUI EL CODI PER FER EL MOTION VECTORS
    #
    # afegir a vector actual_positions totes les coordenades dels blocks de les imatges
    # afegir a vector motion_vector coordenades el block que menor error te del frame anterior
    # afegir a vector errors_prediccio l'error quantitzat !! (func_quantized) que es comet per canviar de block al seguent frame
    #
    # TODO: Use func_quantized for error prediction.
    motion_vector, errors_prediction, _, _, actual_position = block_matching(frame1, frame2, restriccion=True)

    # GENERAR AQUI EL CODI DE VISUALITZACIO
    # crear una línia entre cada posició dels elements dels vectors actual_position i motion_vector que siguin diferents. ex. línia origen (16,32) a (8,32)
    # podeu fer servir  ImageDraw.Draw(img) i ImageDraw.line
    # Create an image
    draw = ImageDraw.Draw(img1)
    block_size = 8
    for (pos, vec) in zip(actual_position, motion_vector):
        if vec != (0, 0):
            orig = (pos[0] + block_size // 2, pos[1] + block_size // 2)  # Center of the block
            new_pos = (orig[0] + vec[0], orig[1] + vec[1])
            draw.line([orig, new_pos], fill="red", width=1)
    img1.show()

    ##################
    ##  DECODIFIER  ##
    ##################

    frame3 = np.zeros(frame1.shape, dtype=np.int16)
    frame4 = np.zeros(frame1.shape, dtype=np.int16)

    # Fill frame3 and frame4 with the motion compensation algorithm
    frame3, frame4 = func_motion_compensation(actual_position, motion_vector, errors_prediction, frame1)

    print("SSIM of frame3-frame2:", metrikz.ssim(frame3, frame2))
    print("SSIM of frame4-frame2:", metrikz.ssim(frame4, frame2))

    ## Show the images
    plt.figure(1, figsize=(16, 10))
    plt.rcParams['image.cmap'] = 'gray'
    plt.subplot(221)
    plt.title("I1-frame anterior")
    plt.imshow(frame1, vmin=0, vmax=255)
    plt.subplot(222)
    plt.title("I2-frame actual")
    plt.imshow(frame2, vmin=0, vmax=255)
    plt.subplot(223)
    plt.title("I3-frame motion compensation")
    plt.imshow(frame3, vmin=0, vmax=255)
    plt.subplot(224)
    plt.title("I4-frame I3 + errors prediction")
    plt.imshow(frame4, vmin=0, vmax=255)

    ## Per mostrar el mapa de calor de les variacions, blau menys error, vermell maxim error
    plt.figure(2, figsize=(14, 14))
    plt.rcParams['image.cmap'] = 'jet'
    plt.subplot(211)
    plt.title("I3 - I2")
    vm = np.max(np.absolute(frame3 - frame2))
    plt.imshow(np.absolute(frame3 - frame2), vmin=0, vmax=vm)  # np.max(np.absolute(frame3-frame2)))
    plt.subplot(212)
    plt.title("I4 - I2")
    plt.imshow(np.absolute(frame4 - frame2), vmin=0, vmax=vm)  # np.max(np.absolute(frame3-frame2)))

    plt.show()


if __name__ == '__main__':
    main()
