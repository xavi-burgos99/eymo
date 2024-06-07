import cv2
import metrikz
import utility
import pylab
import matplotlib.pyplot as plt

def exercise2_1(filename):
	input_file = './videos_y4m/'+ filename +'_cif.y4m'

	for i in ['15', '31', '1', '20', '10']:
		output_file = './videos_mpeg/'+ filename +'_' + i + '.mpeg'

		# Comanda per a la compresio a MPEG1
		command = [
		    'ffmpeg',
		    '-y',
		    '-an',
		    '-i', input_file,
		    '-qscale', i,
		    '-vcodec', 'mpeg1video',
		    output_file,
		]
		utility.execute_command(command)
		
def exercise2_2(filename):
	input_file = './videos_y4m/'+ filename +'_cif.y4m'

	for i in ['15', '31', '1', '20', '10']:
		output_file = './videos_mpeg/'+ filename +'_' + i + '.mpeg'

		# Comanda per a la compresio a MPEG1
		command0 = [
		    'ffmpeg',
		    '-y',
		    '-an',
		    '-i', input_file,
		    '-qscale', i,
		    '-vcodec', 'mpeg1video',
		    output_file,
		]
		utility.execute_command(command0)
		
        # Comanda per a extraure els quadres (frames) del video original
		command_org = [
	         'ffmpeg',
	         '-y',
	         '-i', input_file,
	         './frames/'+ filename +'_original%d.png', 
	    ]
		utility.execute_command(command_org)
		
		command_enc = [
	     'ffmpeg',
	     '-y',
	     '-i', output_file,
	     './frames/'+ filename +'encoded%d.png', 
	    ]
		utility.execute_command(command_enc)
		
		source = cv2.imread('./frames/'+ filename +'original' + str(3) + '.png')
		target = cv2.imread('./frames/'+ filename +'encoded' + str(2) + '.png')
		
		print('MSE video '+ filename +' con un Q-Scale de '+ i +' => '+ metrikz.mse(source, target))

def calcula_metrics_per_video(video_input_file, video_output_file, qscale):
    # Comando para comprimir el video
    command_compression = [
        'ffmpeg',
        '-y',  # Sobrescribe el archivo de salida si ya existe
        '-an',  # No incluye audio
        '-i', video_input_file,
        '-qscale', str(qscale),  # Valor de Q-scale elegido
        '-vcodec', 'mpeg1video',
        video_output_file,
    ]
    utility.execute_command(command_compression)

    # Extrae los cuadros del video original
    command_extract_original = [
        'ffmpeg',
        '-y',
        '-i', video_input_file,
        './frames/original%d.png',
    ]
    utility.execute_command(command_extract_original)

    # Extrae los cuadros del video codificado
    command_extract_encoded = [
        'ffmpeg',
        '-y',
        '-i', video_output_file,
        './frames/encoded%d.png',
    ]
    utility.execute_command(command_extract_encoded)

    # Inicializa listas para almacenar resultados
    mse_values, ssim_values, snr_values = [], [], []
    frames = []

    # Determina el número total de cuadros en el video original
    cap = cv2.VideoCapture(video_input_file)
    N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Recorre los cuadros y calcula las métricas
    for frame_number in range(1, N + 1):
        original_frame_path = './frames/original' + str(frame_number) + '.png'
        encoded_frame_path = './frames/encoded' + str(frame_number) + '.png'

        original_frame = cv2.imread(original_frame_path)
        encoded_frame = cv2.imread(encoded_frame_path)

        mse = metrikz.mse(original_frame, encoded_frame)
        ssim = metrikz.ssim(original_frame, encoded_frame)
        snr = metrikz.snr(original_frame, encoded_frame)

        mse_values.append(mse)
        ssim_values.append(ssim)
        snr_values.append(snr)
        frames.append(frame_number)

    print("All done for video: " + video_input_file)
    return frames, mse_values, ssim_values, snr_values


def ejercicio3(qscale=15):
	# Defineix la llista de vídeos
    video_files = [
        ('./videos_y4m/akiyo_cif.y4m', './videos_mpeg/akiyo_cif.mpeg'),
        ('./videos_y4m/bowing_cif.y4m', './videos_mpeg/bowing_cif.mpeg'),
        ('./videos_y4m/bridge_close_cif.y4m', './videos_mpeg/bridge_close_cif.mpeg'),
        ('./videos_y4m/bridge_far_cif.y4m', './videos_mpeg/bridge_far_cif.mpeg'),
    ]

    # Inicialitza llistes per a dades agregades de tots els vídeos
    all_frames, all_mse, all_ssim, all_snr = [], [], [], []

    # Processa cada vídeo
    for video_input, video_output in video_files:
        frames, mse_values, ssim_values, snr_values = calcula_metrics_per_video(video_input, video_output, qscale)
        all_frames.append(frames)
        all_mse.append(mse_values)
        all_ssim.append(ssim_values)
        all_snr.append(snr_values)

    # Gràfic per MSE
    plt.figure(figsize=(10, 6))
    for i, video_output in enumerate(video_files):
        plt.plot(all_frames[i], all_mse[i], label=video_output[1].split('/')[-1].split('.')[0])
    plt.xlabel('# Quadre')
    plt.ylabel('MSE')
    plt.title('Figura 1: MSE vs. # Quadre')
    plt.legend()
    plt.tight_layout()
    plt.savefig('MSE_per_quadre.png')
    plt.close()

    # Gràfic per SSIM
    plt.figure(figsize=(10, 6))
    for i, video_output in enumerate(video_files):
        plt.plot(all_frames[i], all_ssim[i], label=video_output[1].split('/')[-1].split('.')[0])
    plt.xlabel('# Quadre')
    plt.ylabel('SSIM')
    plt.title('Figura 2: SSIM vs. # Quadre')
    plt.legend()
    plt.tight_layout()
    plt.savefig('SSIM_per_quadre.png')
    plt.close()

    # Gràfic per SNR
    plt.figure(figsize=(10, 6))
    for i, video_output in enumerate(video_files):
        plt.plot(all_frames[i], all_snr[i], label=video_output[1].split('/')[-1].split('.')[0])
    plt.xlabel('# Quadre')
    plt.ylabel('SNR (dB)')
    plt.title('Figura 3: SNR vs. # Quadre')
    plt.legend()
    plt.tight_layout()
    plt.savefig('SNR_per_quadre.png')
    plt.close()

if __name__ == '__main__':
	
    # Pedimos al usuario que ejercicio quiere hacer
	print('Que ejercicio quieres hacer?')
	ej = input('2 o 3: ')
	
	if ej == '2':
		print('Que subapartado quieres hacer?')
		sub = input('1 o 2: ')
		
		# Pedimos al usuario que fichero y4m quiere usar
		print('Que fichero y4m quieres usar?')
		filename = input()
		
		if filename != 'akiyo' and filename != 'bowing' and filename != 'bus' and filename != 'bridge_close' and filename != 'bridge_far':
			print('Fichero no valido')
			exit()
	elif ej == '3':
		print('Que Q-scale quieres usar?')
		qscale = input('1 to 31: ')
		
	if(ej== 2 and sub == '1'):
		exercise2_1(filename)
	elif(ej == 2 and sub == '2'):
		exercise2_2(filename)
	elif(ej == 3):
		ejercicio3(qscale)