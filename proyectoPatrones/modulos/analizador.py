import librosa
import numpy as np
import matplotlib.pyplot as plt
import librosa.display

class AnalizadorPercusion:
    def __init__(self, ruta_audio):
        self.ruta_audio = ruta_audio
        self.y = None
        self.sr = None
        self.cargar_audio()

    def cargar_audio(self):
        print("Cargando audio...")
        self.y, self.sr = librosa.load(self.ruta_audio)

    def bpmYgolpes(self):
        print("detectando transitorios...")
        fuerza_golpes = librosa.onset.onset_strength(y=self.y, sr=self.sr)
        golpes_frames = librosa.onset.onset_detect(onset_envelope=fuerza_golpes, sr=self.sr, delta=0.2, wait=10)
        
        tiempos = librosa.frames_to_time(golpes_frames, sr=self.sr)
        tempo, _ = librosa.beat.beat_track(onset_envelope=fuerza_golpes, sr=self.sr)
        
        bpm = tempo[0] if isinstance(tempo, np.ndarray) else tempo
        return bpm, tiempos

    def graficar_validacion(self, tiempos):
        print("Generando gráfica de validación...")
        plt.figure(figsize=(14, 5))
        librosa.display.waveshow(self.y, sr=self.sr, alpha=0.5, label='Onda de Batería')
        plt.vlines(tiempos, ymin=-1, ymax=1, color='r', alpha=0.8, linestyle='--', label='Golpes Detectados')
        plt.title("Verificación del Reconocimiento de Patrones (Percusión)")
        plt.xlabel("Tiempo (segundos)")
        plt.ylabel("Amplitud de Energía")
        plt.legend()
        plt.show()

    def secuencia_temporal(self, ventana_segundos=10):
        print(f"\nSegmentando audio en ventanas de {ventana_segundos}s...")
        muestras_por_ventana = ventana_segundos * self.sr
        total_ventanas = len(self.y) // muestras_por_ventana
        
        secuencia_datos = []
        for i in range(total_ventanas):
            inicio = i * muestras_por_ventana
            fin = inicio + muestras_por_ventana
            segmento_y = self.y[inicio:fin]
            
            fuerza = librosa.onset.onset_strength(y=segmento_y, sr=self.sr)
            golpes = librosa.onset.onset_detect(onset_envelope=fuerza, sr=self.sr, delta=0.2, wait=10)
            tempo, _ = librosa.beat.beat_track(onset_envelope=fuerza, sr=self.sr)
            
            bpm_segmento = tempo[0] if isinstance(tempo, np.ndarray) else tempo
            tasa_golpes = len(golpes) / ventana_segundos
            
            secuencia_datos.append([bpm_segmento, tasa_golpes])
            
        return secuencia_datos