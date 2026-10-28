import os
import subprocess
import re

class MotorSeparacion:
    def __init__(self, carpeta_base_salida="pistas_separadas"):
        self.carpeta_base_salida = carpeta_base_salida
        self.ruta_salida = None

    def procesar_pista(self, ruta_cancion, callback_progreso=None):
        if not os.path.exists(ruta_cancion):
            raise FileNotFoundError(f"No se encontró el archivo de audio: {ruta_cancion}")

        nombre_cancion = os.path.splitext(os.path.basename(ruta_cancion))[0]
        
        directorio_destino = os.path.join(self.carpeta_base_salida, nombre_cancion)
        os.makedirs(directorio_destino, exist_ok=True)

        print(f"Separando stems para '{nombre_cancion}'...")

        comando = [
            "demucs",
            "-n", "htdemucs",
            "-o", directorio_destino,
            ruta_cancion
        ]

        proceso = subprocess.Popen(
        	comando,
        	stdout=subprocess.PIPE,
        	stderr=subprocess.STDOUT,
        	universal_newlines=True
        )

        patron_procentaje = re.compile(r"(\d+)%")

        for linea in proceso.stdout:
        	print(linea, end="")
        	match = patron_procentaje.search(linea)
        	if match and callback_progreso:
        		porcentaje = int(match.group(1))
        		callback_progreso(porcentaje)
        proceso.wait()
        if proceso.returncode != 0:
        	raise RuntimeError("El proceso de separacion con Demucs fallo")
        
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

        print(f"Separación completada exitosamente.")
        return stems
