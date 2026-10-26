from sklearn.mixture import GaussianMixture
import numpy as np
import matplotlib.pyplot as plt

class PreprocesadorSimbolico:
    def __init__(self, numero_estados=3):
        self.numero_estados = numero_estados
        self.modelo = GaussianMixture(n_components=self.numero_estados, covariance_type='full', random_state=42)
        self.alfabeto = ['A', 'B', 'C', 'D', 'E']

    def transformar(self, secuencia_datos):
        print(f"\nEntrenando modelo Gaussiano sobre {len(secuencia_datos)} vectores...")
        if len(secuencia_datos) < self.numero_estados:
            print("Error: La canción es demasiado corta.")
            return None
            
        matriz = np.array(secuencia_datos)
        
        self.modelo_ia.fit(matriz)
        etiquetas_numericas = self.modelo.predict(matriz)
        
        secuencia_letras = [self.alfabeto[etiqueta] for etiqueta in etiquetas_numericas]
        return "-".join(secuencia_letras)

    def calculos(self, secuencia_datos, limite=10):
        matriz = np.array(secuencia_datos)
        probabilidades = self.modelo.predict_proba(matriz)
        
        print("\n MATRIZ DE PROBABILIDADES GMM ")
        print("Demostración de Soft Clustering:")
        for i in range(min(limite, len(matriz))):
            probs_formateadas = " | ".join([f"{self.alfabeto[j]}: {p*100:.1f}%" for j, p in enumerate(probabilidades[i])])
            
            etiqueta_ganadora = self.alfabeto[np.argmax(probabilidades[i])]
            print(f"[Ventana {i+1} (10s)] {probs_formateadas}  -->  Selección Final: {etiqueta_ganadora}")

    def graficar(self, secuencia_datos):
        matriz = np.array(secuencia_datos)
        etiquetas = self.modelo.predict(matriz)
        
        centroides = self.modelo.means_
        
        print("\nSIGNIFICADO MATEMÁTICO DE LOS SÍMBOLOS (MEDIAS GAUSSIANAS) ---")
        for i in range(self.numero_estados):
            bpm_centro = centroides[i, 0]
            golpes_centro = centroides[i, 1]
            print(f"Símbolo {self.alfabeto[i]} -> Media: {bpm_centro:.1f} BPM, {golpes_centro:.2f} golpes/segundo")
            
        plt.figure(figsize=(10, 6))
        colores = ['blue', 'green', 'red', 'purple', 'orange']
        
        for i in range(self.numero_estados):
            puntos_grupo = matriz[etiquetas == i]
            plt.scatter(puntos_grupo[:, 0], puntos_grupo[:, 1], c=colores[i], label=f'Segmentos tipo {self.alfabeto[i]}', alpha=0.6, s=100)
            plt.scatter(centroides[i, 0], centroides[i, 1], c=colores[i], marker='X', s=250, edgecolors='black')
            
        plt.title("Análisis Estructural")
        plt.xlabel("Velocidad del Segmento")
        plt.ylabel("Densidad Rítmica")
        plt.legend()
        plt.grid(True)
        plt.show()