from sklearn.mixture import GaussianMixture
import numpy as np
import matplotlib.pyplot as plt
import joblib
import os

class PreprocesadorSimbolico:
    def __init__(self, numero_estados=3, ruta_modelo="modelo_gmm.pkl"):
        self.numero_estados = numero_estados
        self.ruta_modelo = ruta_modelo
        self.modelo = GaussianMixture(n_components=self.numero_estados, covariance_type='full', random_state=42)
        self.alfabeto = ['A', 'B', 'C', 'D', 'E']
        self.cargar_modelo()

    def cargar_modelo(self):
        if os.path.exists(self.ruta_modelo):
            try:
                self.modelo = joblib.load(self.ruta_modelo)
                print(f"Se cargo de forma correcta el modelo desde {self.ruta_modelo}")
            except Exception as e:
                print(f"No se pudo cargar el modelo: {e}")
    def guardar_modelo(self):
        joblib.dump(self.modelo, self.ruta_modelo)
        print(f"Modelo guardado en {self.ruta_modelo}")

    
    def configurar_GMM(self, secuencia_datos):

        if len(secuencia_datos) < self.numero_estados:
            return None
        
        mejores_params = optimizar_GMM(secuencia_datos, self.numero_estados)
        self.modelo = GaussianMixture(
            n_components=self.numero_estados,
            covariance_type=mejores_params['covariance_type'],
            max_iter=mejores_params['max_iter'],
            random_state=42
        )

        matriz = np.array(secuencia_datos)
        self.modelo.fit(matriz)
        self.guardar_modelo()
        etiquetas_num = self.modelo.predict(matriz)
        return "_".join([self.alfabeto[e] for e in etiquetas_num])
    
        
    def transformar(self, secuencia_datos):
        print(f"\nEntrenando modelo Gaussiano sobre {len(secuencia_datos)} vectores...")
        if len(secuencia_datos) < self.numero_estados:
            print("Error: La canción es demasiado corta.")
            return None
            
        matriz = np.array(secuencia_datos)
        
        self.modelo.fit(matriz)
        self.guardar_modelo()
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
        
        for i in range(self.numero_estados):
            bpm_centro = centroides[i, 0]
            golpes_centro = centroides[i, 1]
            print(f"Símbolo {self.alfabeto[i]} -> Media: {bpm_centro:.1f} BPM, {golpes_centro:.2f} golpes/segundo")
            
        fig, ax = plt.subplots(figsize=(10, 6))
        fig.patch.set_facecolor('#181818')
        ax.set_facecolor('#181818')
        
        colores = ['blue', 'green', 'red', 'purple', 'orange']
        
        for i in range(self.numero_estados):
            puntos_grupo = matriz[etiquetas == i]
            if len(puntos_grupo) > 0 :
            	ax.scatter(puntos_grupo[:, 0], puntos_grupo[:, 1], c=colores[i], label=f'Segmentos tipo {self.alfabeto[i]}', alpha=0.6, s=100)
            ax.scatter(centroides[i, 0], centroides[i, 1], c=colores[i], marker='X', s=250, edgecolors='black')
            
        ax.set_title("Análisis Estructural", color="#ffffff", fontsize=11)
        ax.set_xlabel("Velocidad del Segmento", color="#a0a0a0", fontsize=9)
        ax.set_ylabel("Densidad Rítmica", color="#a0a0a0", fontsize=9)
        
        ax.tick_params(colors='#a0a0a0')
        ax.spines['bottom'].set_color('#3d3d3d')
        ax.spines['left'].set_color('#3d3d3d')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        ax.legend(facecolor='#181818', edgecolor='none', labelcolor='#ffffff', fontsize=8 )
        fig.tight_layout()
        return fig
