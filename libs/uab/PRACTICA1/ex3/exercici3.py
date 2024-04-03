import os

# Exemple de noms de carpetes i fitxers per a cada imatge seleccionada
imatges = ['Airplane', 'Baboon', 'Boats', 'Goldhill']
formats = ['.ppm', '.pgm', '.jpg', '.jls']  # Afegir .jls als formats d'imatge resultant

# Ruta base on es troben les carpetes d'imatges
base_path = 'Imatges/'

# Diccionari per emmagatzemar les mides dels fitxers i els ràtios de compressió
resultats = {}

# Bucle per a cada imatge seleccionada
for imatge in imatges:
    mides = {}
    for format in formats:
        # Construir la ruta completa del fitxer
        file_path = os.path.join(base_path, imatge, imatge + format)

        # Comprovar si el fitxer existeix i obtenir la seva mida
        if os.path.exists(file_path):
            mides[format] = os.path.getsize(file_path)

    # Calcular el ràtio de compressió per a .jpg i .jls si s'han trobat les mides
    for format_comprimit in ['.jpg', '.jls']:
        if format_comprimit in mides and (('.ppm' in mides) or ('.pgm' in mides)):
            original_format = '.ppm' if '.ppm' in mides else '.pgm'
            ratio = mides[original_format] / mides[format_comprimit]
            resultats[f'{imatge}_{format_comprimit}'] = {'Mides': mides, 'Ràtio de Compressió': ratio}
        else:
            resultats[f'{imatge}_{format_comprimit}'] = {'Mides': mides, 'Ràtio de Compressió': 'No es pot calcular'}

print(resultats)
