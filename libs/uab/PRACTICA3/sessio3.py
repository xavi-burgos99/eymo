import cv2
from scipy.fftpack import dct, idct
from PIL import Image,ImageDraw
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
	return dct(dct(block, axis=0, norm = 'ortho'), axis=1, norm = 'ortho'); 

def idct2(block: np.ndarray) -> np.ndarray:
	"""Compute 2D Inverse Cosine Transform of Image
	Args:
		block (np.ndarray): An image block
	Returns:
		np.ndarray: 2D IDCT of the image block
	"""
	return idct(idct(block, axis=1, norm = 'ortho'), axis=0, norm = 'ortho');

def quantization_process(block: np.ndarray) -> np.ndarray:
	"""Quantization of the DCT coefficients
	Args:
		block (np.ndarray): An image block
	Returns:
		np.ndarray: Quantized image block
	"""
	qm=np.zeros((8, 8))
	for i in range(int(len(block))):
		for j in range(int(len(block))):
			qm[i][j] = np.round(float(block[i][j]) / quantization_matrix[i][j])
	return qm
	
def func_quantized(block):
	"""Quantization of the DCT coefficients
	Args:
		block (np.ndarray): An image block
	Returns:
		np.ndarray: Quantized image block
	"""
	qm=np.zeros((8, 8),dtype=int)  
	qm[:, :] = quantization_process(dct2(block[:,:]))
	return qm

def func_motion_compensation(actual_position: list, motion_vector: list, errors_prediction: list, frame: np.ndarray) -> tuple:
	"""Motion compensation algorithm
	Args:
		actual_position (list): List of actual positions
		motion_vector (list): List of motion vectors
		errors_predicio (list): List of quantized errors
		frame (np.ndarray): The reference frame
	Returns:
		tuple: Tuple with the compensated frame and the frame with the errors
	"""
	frame3 = np.zeros(frame.shape, dtype=np.int16)
	frame4 = np.zeros(frame.shape, dtype=np.int16)
	for i in range(len(actual_position)):
		x, y = actual_position[i]
		xm, ym = motion_vector[i]
		error = errors_prediction[i]
		block = frame[x:x+8, y:y+8]
		block_prev = frame[xm:xm+8, ym:ym+8]
		error_block = np.multiply(block_prev, error)
		block = block + error_block
		frame3[x:x+8, y:y+8] = block
		frame4[x:x+8, y:y+8] = block + error_block
	return frame3, frame4

def main():
	I1 = Image.open("frame0_1.png")		# Old frame
	I2 = Image.open("frame0_2.png")		# New frame

	#I1.show()
	img1 = I1.convert('L')
	img1.save('frame1_gray.png')
	img2 = I2.convert('L')
	img2.save('frame2_gray.png')
	#img1.show()

	frame1 = cv2.imread("frame1_gray.png")
	frame2 = cv2.imread("frame2_gray.png")
	cv2.imshow('image', frame1)
	frame1 = frame1[:, :, 0]
	frame2 = frame2[:, :, 0]

	print("Dimensions de la imatge: ")
	print(frame1.shape)
	dim = frame1.shape
	
	# Final vectors
	actual_position=[]
	motion_vector=[]
	errors_prediction=[]
	   
	# Block generator matrix
	bl=np.zeros((8, 8))


	#
	# GERENAR AQUI EL CODI PER FER EL MOTION VECTORS
	#
	# afegir a vector actual_positions totes les coordenades dels blocks de les imatges
	# afegir a vector motion_vector coordenades el block que menor error te del frame anterior
	# afegir a vector errors_prediccio l'error quantitzat !! (func_quantized) que es comet per canviar de block al seguent frame
	#
	#

	# GENERAR AQUI EL CODI DE VISUALITZACIO
	# crear una línia entre cada posició dels elements dels vectors actual_position i motion_vector que siguin diferents. ex. línia origen (16,32) a (8,32)
	# podeu fer servir  ImageDraw.Draw(img) i ImageDraw.line

	##################
	##  DECODIFIER  ##
	##################
	
	frame3 = np.zeros(frame1.shape, dtype=np.int16)
	frame4 = np.zeros(frame1.shape, dtype=np.int16)

	# Fill frame3 and frame4 with the motion compensation algorithm
	frame3, frame4 = func_motion_compensation(actual_position, motion_vector, errors_prediction, frame1)

	print ("SSIM of frame3-frame2:", metrikz.ssim(frame3, frame2))
	print ("SSIM of frame4-frame2:", metrikz.ssim(frame4, frame2))


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
