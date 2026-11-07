import os
import subprocess
import librosa
import soundfile as sf
import numpy as np
import re
import gc

try:
    import torch
except ImportError:
    torch = None

class MotorSeparacion:
    def __init__(self, carpeta_base_salida="pistas_separadas"):
        self.carpeta_base_salida = carpeta_base_salida
        self.ruta_salida = None


    def volumen_audio(self, ruta_entrada, ruta_salida="separated/temp_normalizado.wav", target_rms_db=-20.0):

        try:
            y, sr = librosa.load(ruta_entrada, sr=None)
        except Exception as e:
            raise ValueError(f"El archivo no se pudo leer. Delate: {str(e)}")
        if y is None or len(y) == 0:
            raise ValueError("El archivo no contiene datos legibles")
        
        rms = np.sqrt(np.mean(y**2))
        if rms == 0:
            return ruta_entrada

        target_rms = 10**(target_rms_db/ 20.0)
        escala = target_rms / rms
        Y_norma = y * escala

        pico_max = np.max(np.abs(Y_norma))
        if pico_max > 1.0:
            Y_norma = Y_norma / pico_max

        os.makedirs(os.path.dirname(ruta_salida), exist_ok=True)
        sf.write(ruta_salida, Y_norma.T if Y_norma.ndim > 1 else Y_norma, sr)

        del y, Y_norma
        gc.collect()
        return ruta_salida

    def procesar_pista(self, ruta_cancion, callback_progreso=None):
        if not os.path.exists(ruta_cancion):
            raise FileNotFoundError(f"No se encontró el archivo de audio: {ruta_cancion}")

        
        nombre_cancion = os.path.splitext(os.path.basename(ruta_cancion))[0]
        ruta_procesada = self.volumen_audio(ruta_cancion, ruta_salida = os.path.join("separated",f"{nombre_cancion}.wav"))
        
        directorio_destino = os.path.join(self.carpeta_base_salida, nombre_cancion)
        os.makedirs(directorio_destino, exist_ok=True)

        print(f"Separando stems para '{nombre_cancion}'...")

        import sys
        comando = [
            sys.executable,
            "-m", "demucs.separate",
            "-n", "htdemucs",
            "-o", directorio_destino,
            ruta_procesada
        ]

        proceso = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )

        patron_porcentaje = re.compile(r"(\d{1,3})%")
        
        try:
            linea_actual= ""
            while True:
                char= proceso.stdout.read(1)
                if not char and proceso.poll() is not None:
                    break
                if char:
                    if char == '\r' or char == '\n':
                        if linea_actual.strip():
                            print(linea_actual)
                            match = patron_porcentaje.search(linea_actual)
                            if match and callback_progreso:
                                porcentaje = int(match.group(1))
                                if 0 <= porcentaje <= 100:
                                    callback_progreso(porcentaje)
                        linea_actual = ""
                    else:
                        linea_actual += char
                        
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
    
        finally:

            if proceso.stdout:
                proceso.stdout.close()
                gc.collect()

                if torch is not None and torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    print("Se libero la caché")
            
