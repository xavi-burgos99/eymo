import cv2
import metrikz
import utility
import pylab
import matplotlib.pyplot as plt

if __name__ == '__main__':
    input_file = './videos_y4m/bus_cif.y4m'

    for i in ['15', '31', '1', '20', '10']:
        output_file = './videos_mpeg/bus_cif_' + i + '.mpeg'

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