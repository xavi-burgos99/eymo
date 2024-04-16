nombre_pixels = 21 * (10**6)  # 21 milions de píxels
dades_per_pixel = 24  # 8 bits per canal de color, 3 canals

# Càlcul del pes total en bits
pes_total_bits = nombre_pixels * dades_per_pixel

# Convertim a bytes, KB i MB
pes_total_bytes = pes_total_bits / 8
pes_total_KB = pes_total_bytes / 1024
pes_total_MB = pes_total_KB / 1024

print(pes_total_MB)
