import cv2
import matplotlib.pyplot as plt
import metrikz  # Assumeix que tens una llibreria anomenada metrikz que pot calcular SSIM
import utility


def calcula_ssim_per_video(video_input_file, video_output_file, qscale):
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
    ssim_values = []
    frames = []

    # Determina el número total de cuadros en el video original
    cap = cv2.VideoCapture(video_input_file)
    N = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Recorre los cuadros y calcula SSIM
    for frame_number in range(1, N+1):  # Ajuste para incluir el último cuadro
        original_frame_path = './frames/original' + str(frame_number) + '.png'
        encoded_frame_path = './frames/encoded' + str(frame_number) + '.png'

        original_frame = cv2.imread(original_frame_path)
        encoded_frame = cv2.imread(encoded_frame_path)

        ssim = metrikz.ssim(original_frame, encoded_frame)
        ssim_values.append(ssim)
        frames.append(frame_number)

    return frames, ssim_values


if __name__ == '__main__':
    # Defineix la llista de vídeos
    video_files = [
        ('./videos_y4m/akiyo_cif.y4m', 'akiyo_cif.mpeg'),
        ('./videos_y4m/bowing_cif.y4m', 'bowing_cif.mpeg'),
        ('./videos_y4m/bridge_close_cif.y4m', 'bridge_close_cif.mpeg'),
        ('./videos_y4m/bridge_far_cif.y4m', 'bridge_far_cif.mpeg'),
    ]

    # Valor de Q-scale escollit
    qscale = 15

    plt.figure()

    # Processa cada vídeo
    for video_input, video_output in video_files:
        frames, ssim_values = calcula_ssim_per_video(video_input, video_output, qscale)
        plt.plot(frames, ssim_values, label=video_output.split('.')[0])

    plt.xlabel('# Quadre')
    plt.ylabel('SSIM')
    plt.title('SSIM vs. # Quadre')
    plt.legend()
    plt.show()
