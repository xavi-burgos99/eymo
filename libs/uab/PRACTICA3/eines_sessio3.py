"""
Eines auxiliars per fer la practica

For usage and a list of options, try this:
$ ./eines_sessio3 -h"""

import metrikz
import numpy as np
from scipy.fftpack import dct, idct


quantization_matrix =  [[16.,11.,10.,16.,24.,40.,51.,61.],
                        [12.,12.,14.,19.,26.,58.,60.,55.],
                        [14.,13.,16.,24.,40.,57.,69.,56.],
                        [14.,17.,22.,29.,51.,87.,80.,62.],
                        [18.,22.,37.,56.,68.,109.,103.,77.],
                        [24.,35.,55.,64.,81.,104.,113.,92.],
                        [49.,64.,78.,87.,103.,121.,120.,101.],
                        [72.,92.,95.,98.,112.,100.,103.,99.]]


__author__ = "Jordi Serra Ruiz <jordi.serra@uab.cat>"
__copyright__ = "Copyright (c) 2019 Jordi Serra"
__license__ = "Copyright (c)"


#contador de repeticions
def func_encoded_values(errors):
    encoded_values=[]
    prev=errors[0]
    cont=1
 
    for i in range(1,len(errors)):
        if prev != errors[i]:
            encoded_values.append(cont)
            encoded_values.append(prev)
            prev=errors[i]
            cont=1
        else:
            cont=cont+1
    encoded_values.append(cont)
    encoded_values.append(prev)
    return encoded_values


#algoritme ZIG-ZAG
def zigzag(data):
    """Retorna l'ordre de la matriu d'error en zigzag.
    value = zigzag(data)
    Parameters
    ----------
    data      : matriu d'errors de 8x8.
    Return
    ----------
    value     : vector amb ordre en zigzag
    """
    result = [data[0][0], data[0][1], data[1][0], data[2][0], data[1][1], data[0][2], data[0][3], data[1][2], data[2][1], data[3][0], data[4][0], data[3][1], data[2][2], data[1][3], data[0][4], data[0][5], data[1][4], data[2][3], data[3][2], data[4][1], data[5][0], data[6][0], data[5][1], data[4][2], data[3][3], data[2][4], data[1][5], data[0][6], data[0][7], data[1][6], data[2][5], data[3][4], data[4][3], data[5][2], data[6][1], data[7][0], data[7][1], data[6][2], data[5][3], data[4][4], data[3][5], data[2][6], data[1][7], data[2][7], data[3][6], data[4][5], data[5][4], data[6][3], data[7][2], data[7][3], data[6][4], data[5][5], data[4][6], data[3][7], data[4][7], data[5][6], data[6][5], data[7][4], data[7][5], data[6][6], data[5][7], data[6][7], data[7][6], data[7][7]]
    return result



