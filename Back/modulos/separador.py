import os
import subprocess
import librosa
import soundfile as sf
import numpy as np
import re
import gc
import sys
import contextlib

from modulos import config
from modulos.seguridad import sanitizar_nombre, ruta_dentro_de, validar_audio, ocultar_ruta

try:
    import torch
except ImportError:
    torch = None

_PATRON_PORCENTAJE = re.compile(r"(\d{1,3})%")


class _EscritorProgreso:
    """Sustituye a stderr/stdout mientras Demucs corre dentro del mismo proceso
    (modo ejecutable). Lee el % que imprime tqdm y lo manda al callback."""

    def __init__(self, callback):
        self.callback = callback
        self.destino = sys.stderr  # normalmente el archivo de log

    def write(self, texto):
        coincidencias = _PATRON_PORCENTAJE.findall(texto)
        if coincidencias and self.callback:
            porcentaje = int(coincidencias[-1])
            if 0 <= porcentaje <= 100:
                self.callback(porcentaje)
        elif self.destino is not None and texto.strip():
            try:
                self.destino.write(texto if texto.endswith("\n") else texto + "\n")
            except Exception:
                pass
        return len(texto)

    def flush(self):
        pass

    def isatty(self):
        return False


class MotorSeparacion:
    def __init__(self, carpeta_base_salida=None):
        self.carpeta_base_salida = carpeta_base_salida or config.CARPETA_STEMS
        self.ruta_salida = None

    def volumen_audio(self, ruta_entrada, ruta_salida=None, target_rms_db=-20.0):

        ruta_salida = ruta_salida or os.path.join(config.CARPETA_TEMPORAL, "temp_normalizado.wav")
        try:
            y, sr = librosa.load(ruta_entrada, sr=None)
        except Exception as e:
            raise ValueError(f"El archivo no se pudo leer. Detalle: {ocultar_ruta(e)}")
        if y is None or len(y) == 0:
            raise ValueError("El archivo no contiene datos legibles")

        rms = np.sqrt(np.mean(y**2))
        if rms == 0:
            return ruta_entrada

        target_rms = 10**(target_rms_db / 20.0)
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

    # ------------------------------------------------------------------ Demucs
    def _demucs_subproceso(self, ruta_audio, destino, callback_progreso):
        """Modo desarrollo: `python -m demucs.separate` en un proceso aparte."""
        comando = [sys.executable, "-m", "demucs.separate", "-n", "htdemucs", "-o", destino, ruta_audio]
        proceso = subprocess.Popen(comando, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                   text=True, bufsize=1)
        try:
            linea_actual = ""
            while True:
                char = proceso.stdout.read(1)
                if not char and proceso.poll() is not None:
                    break
                if char:
                    if char == '\r' or char == '\n':
                        if linea_actual.strip():
                            print(linea_actual)
                            match = _PATRON_PORCENTAJE.search(linea_actual)
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
        finally:
            if proceso.stdout:
                proceso.stdout.close()

    def _demucs_en_proceso(self, ruta_audio, destino, callback_progreso):
        """Modo ejecutable: dentro del .exe `sys.executable` ES la aplicación, así que
        lanzar `-m demucs.separate` abriría otra copia de la ventana en lugar de Demucs.
        Por eso aquí se llama a Demucs directamente, como librería."""
        from demucs.separate import main as demucs_main
        escritor = _EscritorProgreso(callback_progreso)
        try:
            with contextlib.redirect_stderr(escritor), contextlib.redirect_stdout(escritor):
                demucs_main(["-n", "htdemucs", "-o", destino, ruta_audio])
        except SystemExit as salida:  # Demucs usa sys.exit() para sus errores
            if salida.code not in (0, None):
                raise RuntimeError("El proceso de separacion con Demucs fallo")

    def _localizar_stems(self, directorio_destino):
        def encontrar_stem(nombre_stem):
            for raiz, _, archivos in os.walk(directorio_destino):
                if f"{nombre_stem}.wav" in archivos:
                    return os.path.join(raiz, f"{nombre_stem}.wav")
            raise FileNotFoundError(f"No se encontró el stem {nombre_stem}.wav tras la separación")

        return {
            "bateria": encontrar_stem("drums"),
            "voz": encontrar_stem("vocals"),
            "bajo": encontrar_stem("bass"),
            "otros": encontrar_stem("other"),
        }

    # ------------------------------------------------------------------ API
    def procesar_pista(self, ruta_cancion, callback_progreso=None):
        ruta_cancion = validar_audio(ruta_cancion, config.TAMANO_MAX_AUDIO_MB)

        nombre_cancion = os.path.splitext(sanitizar_nombre(os.path.basename(ruta_cancion)))[0]
        ruta_procesada = self.volumen_audio(
            ruta_cancion,
            ruta_salida=ruta_dentro_de(config.CARPETA_TEMPORAL, f"{nombre_cancion}.wav"))

        directorio_destino = ruta_dentro_de(self.carpeta_base_salida, nombre_cancion)
        os.makedirs(directorio_destino, exist_ok=True)

        print("Separando stems...")

        try:
            if config.EMPAQUETADO:
                self._demucs_en_proceso(ruta_procesada, directorio_destino, callback_progreso)
            else:
                self._demucs_subproceso(ruta_procesada, directorio_destino, callback_progreso)

            self.ruta_salida = directorio_destino
            stems = self._localizar_stems(directorio_destino)
            print("Separación completada exitosamente.")
            return stems

        finally:
            try:
                if os.path.isfile(ruta_procesada) and ruta_procesada != ruta_cancion:
                    os.remove(ruta_procesada)
            except OSError:
                pass

            gc.collect()
            if torch is not None and torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("Se libero la caché")
