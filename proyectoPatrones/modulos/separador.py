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

        print(f"[*] [Motor IA] Separando stems para '{nombre_cancion}'...")

        comando = [
            "demucs",
            "-n", "htdemucs",
            "-o", directorio_destino,
            ruta_cancion
        ]

        subprocess.run(comando, check=True)

        self.ruta_salida = directorio_destino

        def encontrar_stem(nombre_stem):
            for raiz, _, archivos in os.walk(directorio_destino):
                if f"{nombre_stem}.wav" in archivos:
                    return os.path.join(raiz, f"{nombre_stem}.wav")
            raise FileNotFoundError(f"No se encontró el archivo {nombre_stem}.wav en {directorio_destino}")

        stems = {
            "bateria": encontrar_stem("drums"),
            "voz": encontrar_stem("vocals"),
            "bajo": encontrar_stem("bass"),
            "otros": encontrar_stem("other")
        }

        print(f"[+] [Motor IA] Separación completada exitosamente.")
        return stems