import librosa
import numpy as np

class AnalizadorBajo:
    def __init__(self, ruta_audio):
        self.ruta_audio = ruta_audio
        self.y = None
        self.sr = None
        self._cargar_audio()

    def _cargar_audio(self):
        print("Analizando bajo...")
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
            
            f0, _, _ = librosa.pyin(
                segmento_y, 
                fmin=librosa.note_to_hz('C1'), 
                fmax=librosa.note_to_hz('D4'), 
                sr=self.sr
            )
            f0_valido = f0[~np.isnan(f0)] if f0 is not None else []
            frecuencia_media = float(np.mean(f0_valido)) if len(f0_valido) > 0 else 0.0
            
            rms = librosa.feature.rms(y=segmento_y)[0]
            energia = float(np.mean(rms))
            
            umbral_silencio = 0.01
            if energia < umbral_silencio:
                frecuencia_media = 0.0
                energia = 0.0
                
            secuencia_datos.append([frecuencia_media, energia])
            
        print(f"[+] Se generaron {len(secuencia_datos)} vectores de bajo.")
        return secuencia_datos