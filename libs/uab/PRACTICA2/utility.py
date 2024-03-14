import pylab
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os
import subprocess

# Visualisar la diferencie entre 2 imagenes como heatmap
# Cuando la segunda imagen tiene una diferente sistema de coordenadas,
# se puede utilizar el tercer parametro para voltear la imagen
# Fuente de la funcion: http://www.pmavridis.com/misc/heatmaps/
def heatmap(image_1_path, image_2_path, flip_output=False):
    input = mpimg.imread(image_1_path)
    output = mpimg.imread(image_2_path)
    
    if flip_output:
        output = np.flipud(output)

    # Calculate the absolute difference on each channel separately
    error_r = np.fabs(np.subtract(output[:,:,0], input[:,:,0]))
    error_g = np.fabs(np.subtract(output[:,:,1], input[:,:,1]))
    error_b = np.fabs(np.subtract(output[:,:,2], input[:,:,2]))

    # Calculate the maximum error for each pixel
    lum_img = np.maximum(np.maximum(error_r, error_g), error_b)

    # Uncomment the next line to turn the colors upside-down
    #lum_img = np.negative(lum_img);

    imgplot = plt.imshow(lum_img)

    # Choose a color palette
    imgplot.set_cmap('jet')
    #imgplot.set_cmap('Spectral') 

    plt.colorbar()
    plt.axis('off')

    pylab.show()
    
# Executar la comanda en un proceso del sistema
# Para ver la salida de la comanda (como en un terminal),
# solo hay que pasar el segundo parametro igual a True
def execute_command(command, output_results=False):

    if output_results:
        command_string = ""

        for item in command:
            command_string += str(item) + " "
            
        os.system(command_string)
    else:
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(command, stdout=devnull, stderr=subprocess.STDOUT)
    