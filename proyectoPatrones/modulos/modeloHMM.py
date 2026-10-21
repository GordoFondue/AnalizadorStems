import numpy as np
from hmmlearn.hmm import CategoricalHMM

class ClasificadorEstructuraHMM:
    def __init__(self, numero_estados_ocultos=3):
        self.numero_estados_ocultos = numero_estados_ocultos
        self.mapeo_simbolos = {
            'A': 0, 'B': 1, 'C': 2, 'D': 3, 'E': 4,
            'X': 5, 'Y': 6, 'Z': 7,
            'B1': 8, 'B2': 9, 'B3': 10,
            'O1': 11, 'O2': 12, 'O3': 13
        }
        self.modelos_por_genero = {}

    def _cadena_a_vector(self, cadena_simbolica):
        """Convierte una cadena tipo 'A-B-C' a una matriz numérica 2D para hmmlearn."""
        simbolos = cadena_simbolica.split('-')
        indices = [self.mapeo_simbolos[s] for s in simbolos if s in self.mapeo_simbolos]
        if not indices:
            return None
        return np.array(indices).reshape(-1, 1)

    def entrenar_modelos(self, registros_bd):
        """
        Entrena un HMM por género utilizando los registros recuperados de SQLite.
        registros_bd: lista de tuplas (sintaxis_bateria, sintaxis_voz, sintaxis_bajo, sintaxis_otros, genero)
        """
        datos_por_genero = {}

        for r in registros_bd:
            cadena_bat, cadena_voz, cadena_bajo, cadena_otros, genero = r
            cadena_unificada = f"{cadena_bat}-{cadena_voz}-{cadena_bajo}-{cadena_otros}"
            
            if genero not in datos_por_genero:
                datos_por_genero[genero] = []
            
            vec = self._cadena_a_vector(cadena_unificada)
            if vec is not None:
                datos_por_genero[genero].append(vec)

        for genero, secuencias in datos_por_genero.items():
            if not secuencias:
                continue
            
            X = np.concatenate(secuencias)
            lengths = [len(seq) for seq in secuencias]
            n_features = len(self.mapeo_simbolos)

            modelo = CategoricalHMM(
                n_components=self.numero_estados_ocultos,
                n_features=n_features,
                n_iter=100,
                random_state=42
            )
            modelo.fit(X, lengths)
            self.modelos_por_genero[genero] = modelo
            print(f"[+] [HMM] Modelo entrenado con éxito para el género: '{genero}' ({len(secuencias)} pistas)")

    def predecir_genero(self, cadena_bat, cadena_voz, cadena_bajo, cadena_otros):
        if not self.modelos_por_genero:
            return "Sin modelos entrenados", {}

        cadena_unificada = f"{cadena_bat}-{cadena_voz}-{cadena_bajo}-{cadena_otros}"
        X = self._cadena_a_vector(cadena_unificada)

        if X is None:
            return "Cadena inválida", {}

        scores = {}
        for genero, modelo in self.modelos_por_genero.items():
            try:
                scores[genero] = float(modelo.score(X))
            except Exception:
                scores[genero] = float('-inf')

        genero_predicho = max(scores, key=scores.get)
        return genero_predicho, scores