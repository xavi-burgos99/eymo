import cv2
import metrikz
import utility
import pylab
import matplotlib.pyplot as plt


if __name__ == '__main__':
	# Noms dels arxius d'entrada i sortida. Excemples
	video_input_file = './bridge_far_cif.y4m'
	video_output_file = 'bridge_far_cif.mpeg'

	# Comanda per a la compresio a MPEG1
	command = [
	    'ffmpeg',
	    '-y',
	    '-an',
	    '-i', video_input_file, 
	    '-qscale', '15',
	    '-vcodec', 'mpeg1video',
	    video_output_file,
	]

	# Executem la comanda
	utility.execute_command(command)

	# Comanda per a extraure els quadres (frames) del video original
	command = [
	     'ffmpeg',
	     '-y',
	     '-i', video_input_file,
	     './frames/original%d.png', 
	 ]

	utility.execute_command(command)

	# Comanda per a extreure els quadres del video codificat
	command = [
	     'ffmpeg',
	     '-y',
	     '-i', video_output_file,
	     './frames/encoded%d.png', 
	 ]

	utility.execute_command(command)
	
	# Exemple per lleguir 1 imagatge i comparala amb la codificada, i calcular la metrica de SSIM entre les dues
	source = cv2.imread('./frames/original' + str(3) + '.png')
	target = cv2.imread('./frames/encoded' + str(2) + '.png')

	print(metrikz.ssim(source, target))
