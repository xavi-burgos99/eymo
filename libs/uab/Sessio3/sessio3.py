#from scipy import misc
import cv2
from scipy.fftpack import dct, idct
from PIL import Image,ImageDraw  # necessari tenir instalar llibreria PILLOW
import numpy as np
import metrikz
import time


quantization_matrix =  [[16.,11.,10.,16.,24.,40.,51.,61.],
                        [12.,12.,14.,19.,26.,58.,60.,55.],
                        [14.,13.,16.,24.,40.,57.,69.,56.],
                        [14.,17.,22.,29.,51.,87.,80.,62.],
                        [18.,22.,37.,56.,68.,109.,103.,77.],
                        [24.,35.,55.,64.,81.,104.,113.,92.],
                        [49.,64.,78.,87.,103.,121.,120.,101.],
                        [72.,92.,95.,98.,112.,100.,103.,99.]]



def dct2(block):
    return dct(dct(block, axis=0, norm = 'ortho'), axis=1, norm = 'ortho'); 
                   



def idct2(block):
    return idct(idct(block, axis=1, norm = 'ortho'), axis=0, norm = 'ortho');
    
    
    

def quantization_process(block):
    qm=np.zeros((8, 8))
    for i in range(int(len(block))):
        for j in range(int(len(block))):
            qm[i][j] = np.round( float(block[i][j]) / quantization_matrix[i][j])
    return qm
    
    

# Aplicar DCT y llamar la funcion de cuantizacion pel vector dels errors.
def func_quantized(block):
    qm=np.zeros((8, 8),dtype=int)  
    qm[:,:] = quantization_process(dct2(block[:,:]))
    return qm


# El inverso de la operacion anterior
def func_inverse(block):
    inverse = inverse_process(block)
    inverse = round(idct2(block_struct.data * quantization_matrix));



# Funció per crear l'algoritme de motion compensation. DECODIFICADOR
def func_motion_compensation(actual_position, motion_vector, errors_predicio):

    ## 
    ## Implementar motion compensation.
    ## Crear frame3 a partir de frame1 i MV
    ## i despres crear frame4 i corregir amb errors de prediccio
    ## tenint en compte que estan en el format adient de la matriu d'errors.
    ## (aplicar procés invers de la sessió 2 amb els errors de predicció.
    ##

    return 0





if __name__ == '__main__':

    #frame anterior
    I1 = Image.open("frame0_1.png")
    #frame actual
    I2 = Image.open("frame0_2.png")

#   I1.show()
    img1 = I1.convert('L')
    img1.save('frame1_gray.png')
    img2 = I2.convert('L')
    img2.save('frame2_gray.png')
#   img1.show()
   
    frame1 = cv2.imread("frame1_gray.png")
    frame2 = cv2.imread("frame2_gray.png")
    cv2.imshow('image',frame1)
    frame1=frame1[:,:,0]
    frame2=frame2[:,:,0]
  
    print("dimensions de la imatge= "  )
    print(frame1.shape)
    dim=frame1.shape
    
    #vectors finals
    actual_position=[]
    motion_vector=[]
    errors_prediction=[]
       
    # matriu per generar els blocs 
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
    
    
    
    
    #############################
    ###
    ### DECODIFICADOR 
    ###
    #############################
    
    frame3 = np.zeros(frame1.shape,dtype=np.int16)
    frame4 = np.zeros(frame1.shape,dtype=np.int16)
    
    # crida a funcio metode motion compensation
    func_motion_compensation(actual_position, motion_vector, errors_prediction)

    print ("ssim frame3,frame2:", metrikz.ssim(frame3,frame2))
    print ("ssim frame4,frame2:", metrikz.ssim(frame4,frame2))


    ## Per mostrar per pantalla les quatre imatges.
    plt.figure(1,figsize=(16,10))
    plt.rcParams['image.cmap'] = 'gray'
    plt.subplot(221)
    plt.title("I1-frame anterior")
    plt.imshow(frame1,vmin=0,vmax=255)
    plt.subplot(222)
    plt.title("I2-frame actual")
    plt.imshow(frame2,vmin=0,vmax=255)
    plt.subplot(223)
    plt.title("I3-frame motion compensation")
    plt.imshow(frame3,vmin=0,vmax=255)
    plt.subplot(224)
    plt.title("I4-frame I3 + errors prediction")
    plt.imshow(frame4,vmin=0,vmax=255)

## Per mostrar el mapa de calor de les variacions, blau menys error, vermell maxim error
    plt.figure(2,figsize=(14,14))
    plt.rcParams['image.cmap'] = 'jet'
    plt.subplot(211)
    plt.title("I3 - I2")
    vm=np.max(np.absolute(frame3-frame2))
    plt.imshow(np.absolute(frame3-frame2),vmin=0,vmax=vm)#np.max(np.absolute(frame3-frame2)))
    plt.subplot(212)
    plt.title("I4 - I2")
    plt.imshow(np.absolute(frame4-frame2),vmin=0,vmax=vm)#np.max(np.absolute(frame3-frame2)))

    plt.show()

    
    
