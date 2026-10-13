import librosa
import numpy as np

class AnalizadorVoz:
    def __init__(self, ruta_audio):
        self.ruta_audio = ruta_audio
        self.y = None
        self.sr = None
        self._cargar_audio()

    def _cargar_audio(self):
        print(" Cargando onda vocal en memoria...")
        self.y, self.sr = librosa.load(self.ruta_audio)

    def extraer_secuencia_temporal(self, ventana_segundos=10):
        print(f"\nSegmentando audio en ventanas de {ventana_segundos}s...")
        muestras_por_ventana = ventana_segundos * self.sr
        total_ventanas = len(self.y) // muestras_por_ventana
        
        secuencia_datos = []
        for i in range(total_ventanas):
            inicio = i * muestras_por_ventana
            fin = inicio + muestras_por_ventana
            segmento_y = self.y[inicio:fin]
            
            rms = librosa.feature.rms(y=segmento_y)[0]
            energia = np.mean(rms)
            
            zcr = librosa.feature.zero_crossing_rate(segmento_y)[0]
            textura = np.mean(zcr)
            umbral_silencio = 0.015  
            if energia < umbral_silencio:
                energia = 0.0
                textura = 0.0
            secuencia_datos.append([energia, textura])
            
        print(f"[+] Se generaron {len(secuencia_datos)} vectores vocales.")
        return secuencia_datos