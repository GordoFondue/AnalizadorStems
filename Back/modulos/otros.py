import librosa
import numpy as np

class AnalizadorOtros:
    def __init__(self, ruta_audio):
        self.ruta_audio = ruta_audio
        self.y = None
        self.sr = None
        self.cargar_audio()

    def cargar_audio(self):
        print("Cargando pista instrumental armónica...")
        self.y, self.sr = librosa.load(self.ruta_audio)

    def secuencia_temporal(self, ventana_segundos=10):
        print(f"\n Segmentando audio en ventanas de {ventana_segundos}s...")
        muestras_por_ventana = ventana_segundos * self.sr
        total_ventanas = len(self.y) // muestras_por_ventana
        
        secuencia_datos = []
        for i in range(total_ventanas):
            inicio = i * muestras_por_ventana
            fin = inicio + muestras_por_ventana
            segmento_y = self.y[inicio:fin]
            
            mfccs = librosa.feature.mfcc(y=segmento_y, sr=self.sr, n_mfcc=13)
            mfcc_1 = float(np.mean(mfccs[0]))
            
            centroide = librosa.feature.spectral_centroid(y=segmento_y, sr=self.sr)[0]
            brillo_medio = float(np.mean(centroide))
            
            rms = librosa.feature.rms(y=segmento_y)[0]
            if np.mean(rms) < 0.01:
                mfcc_1 = 0.0
                brillo_medio = 0.0
                
            secuencia_datos.append([mfcc_1, brillo_medio])
            
        return secuencia_datos