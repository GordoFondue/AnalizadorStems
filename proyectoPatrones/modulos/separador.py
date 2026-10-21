import os
import subprocess

class MotorSeparacion:
    def __init__(self, carpeta_base_salida="pistas_separadas"):
        self.carpeta_base_salida = carpeta_base_salida
        self.ruta_salida = None

    def procesar_pista(self, ruta_cancion):
        if not os.path.exists(ruta_cancion):
            raise FileNotFoundError(f"No se encontró el archivo de audio: {ruta_cancion}")

        nombre_cancion = os.path.splitext(os.path.basename(ruta_cancion))[0]
        
        directorio_destino = os.path.join(self.carpeta_base_salida, nombre_cancion)
        os.makedirs(directorio_destino, exist_ok=True)

        print(f"Separando stems para '{nombre_cancion}' en: {directorio_destino}...")

        comando = [
            "demucs",
            "-n", "htdemucs",
            "-o", directorio_destino,
            "--filename", "{stem}.{ext}",  
            ruta_cancion
        ]

        subprocess.run(comando, check=True)
        carpeta_stems_generados = os.path.join(directorio_destino, "htdemucs", nombre_cancion)
        self.ruta_salida = directorio_destino
        
        stems = {
            "bateria": os.path.join(directorio_destino, "drums.wav") if os.path.exists(os.path.join(directorio_destino, "drums.wav")) else os.path.join(carpeta_stems_generados, "drums.wav"),
            "voz": os.path.join(directorio_destino, "vocals.wav") if os.path.exists(os.path.join(directorio_destino, "vocals.wav")) else os.path.join(carpeta_stems_generados, "vocals.wav"),
            "bajo": os.path.join(directorio_destino, "bass.wav") if os.path.exists(os.path.join(directorio_destino, "bass.wav")) else os.path.join(carpeta_stems_generados, "bass.wav"),
            "otros": os.path.join(directorio_destino, "other.wav") if os.path.exists(os.path.join(directorio_destino, "other.wav")) else os.path.join(carpeta_stems_generados, "other.wav")
        }

        print(f"[+] [Motor IA] Separación completada exitosamente.")
        return stems