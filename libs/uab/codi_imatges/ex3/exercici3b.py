import os
import pandas as pd

# Noms de les imatges i formats d'interès
imatges = ['Airplane', 'Baboon', 'Boats', 'Goldhill']
formats_compressio = ['.jpg', '.jls']
resolucions = ['', '_2', '_4']  # Original, 1/2, 1/4

# Ruta base on es troben les carpetes d'imatges
base_path = 'Imatges/'

# Diccionari per emmagatzemar els resultats
resultats = {imatge: {} for imatge in imatges}

# Bucle per a cada imatge i resolució
for imatge in imatges:
    for res in resolucions:
        nom_imatge_res = imatge + res
        for format_comprimit in formats_compressio:
            mides = {}

            # Buscar el fitxer original (.ppm o .pgm)
            for format_original in ['.ppm', '.pgm']:
                file_path_original = os.path.join(base_path, imatge, nom_imatge_res + format_original)
                if os.path.exists(file_path_original):
                    mides['original'] = os.path.getsize(file_path_original)
                    break

            # Buscar el fitxer comprimit (.jpg o .jls)
            file_path_comprimit = os.path.join(base_path, imatge, nom_imatge_res + format_comprimit)
            if os.path.exists(file_path_comprimit):
                mides['comprimit'] = os.path.getsize(file_path_comprimit)

            # Calcular el ràtio de compressió si s'han trobat ambdues mides
            if 'original' in mides and 'comprimit' in mides:
                ràtio = mides['original'] / mides['comprimit']
                clau = f'{format_comprimit[-3:]}_Res{res or "1"}'
                resultats[imatge][clau] = ràtio

# Convertir els resultats en un DataFrame per a una presentació més clara
df_resultats = pd.DataFrame(resultats).T  # Transposar per tenir les imatges com a files
print(df_resultats)
