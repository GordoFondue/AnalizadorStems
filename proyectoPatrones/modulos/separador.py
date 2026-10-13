import subprocess
import os
import sys

class MotorSeparacion:
    def __init__(self, modelo="htdemucs"):
        self.modelo = modelo
        self.ruta_salida = "separated"

    def procesar_pista(self, ruta_mp3):
        if not os.path.exists(ruta_mp3):
            raise FileNotFoundError(f"El archivo '{ruta_mp3}' no existe. Asegúrate de incluir la extensión o la ruta correcta.")

        print(f"[*] [Motor IA] Iniciando separación con modelo {self.modelo}...")
        comando = [sys.executable, "-m", "demucs", "-n", self.modelo, ruta_mp3]
        
        try:
            subprocess.run(comando, check=True)
            print("[+] [Motor IA] Separación completada.")
            return self._generar_rutas(ruta_mp3)
        except subprocess.CalledProcessError as e:
            print(f"[-] [Motor IA] Error crítico en la ejecución: {e}")
            return None

    def _generar_rutas(self, ruta_mp3):
        nombre_base = os.path.splitext(os.path.basename(ruta_mp3))[0]
        ruta_base = os.path.join(self.ruta_salida, self.modelo, nombre_base)
        
        return {
            "bateria": os.path.join(ruta_base, "drums.wav"),
            "bajo": os.path.join(ruta_base, "bass.wav"),
            "voz": os.path.join(ruta_base, "vocals.wav"),
            "otros": os.path.join(ruta_base, "other.wav")
        }