import os
from modulos.separador import MotorSeparacion
from modulos.analizador import AnalizadorPercusion
from modulos.voz import AnalizadorVoz
from modulos.bajo import AnalizadorBajo
from modulos.otros import AnalizadorOtros
from modulos.simbolico import PreprocesadorSimbolico
from modulos.database import GestorBaseDatos
from modulos.modeloHMM import ClasificadorEstructuraHMM

class ControladorAnalisis:
    
    def __init__(self, carpeta_salida="pistas_separadas", ruta_db="patrones_musicales.db"):
        self.separador = MotorSeparacion(carpeta_base_salida=carpeta_salida)
        self.db = GestorBaseDatos(ruta_db=ruta_db)

    def procesar_audio(self, ruta_mp3: str) -> dict:
        if not os.path.exists(ruta_mp3):
            raise FileNotFoundError(f"El archivo de audio no existe: {ruta_mp3}")

        rutas_stems = self.separador.procesar_pista(ruta_mp3)

        analizador_perc = AnalizadorPercusion(rutas_stems["bateria"])
        bpm, tiempos = analizador_perc.extraer_bpm_y_golpes()
        sec_bateria = analizador_perc.extraer_secuencia_temporal(ventana_segundos=10)
        
        sim_bat = "A"
        if sec_bateria:
            traductor_bat = PreprocesadorSimbolico(numero_estados=3)
            sim_bat = traductor_bat.transformar_a_simbolos(sec_bateria) or "A"

        analizador_v = AnalizadorVoz(rutas_stems["voz"])
        sec_voz = analizador_v.extraer_secuencia_temporal(ventana_segundos=10)
        
        sim_voz = "A"
        if sec_voz:
            traductor_voz = PreprocesadorSimbolico(numero_estados=3)
            traductor_voz.alfabeto = ['X', 'Y', 'Z']
            sim_voz = traductor_voz.transformar_a_simbolos(sec_voz) or "A"

        analizador_b = AnalizadorBajo(rutas_stems["bajo"])
        sec_bajo = analizador_b.extraer_secuencia_temporal(ventana_segundos=10)
        
        sim_bajo = "A"
        if sec_bajo:
            traductor_bajo = PreprocesadorSimbolico(numero_estados=3)
            traductor_bajo.alfabeto = ['B1', 'B2', 'B3']
            sim_bajo = traductor_bajo.transformar_a_simbolos(sec_bajo) or "A"

        analizador_o = AnalizadorOtros(rutas_stems["otros"])
        sec_otros = analizador_o.extraer_secuencia_temporal(ventana_segundos=10)
        
        sim_otros = "A"
        if sec_otros:
            traductor_otros = PreprocesadorSimbolico(numero_estados=3)
            traductor_otros.alfabeto = ['O1', 'O2', 'O3']
            sim_otros = traductor_otros.transformar_a_simbolos(sec_otros) or "A"

        registros = self.db.entrenamiento()
        genero_predicho = "Entrenamiento"
        probabilidades = {}

        if registros:
            hmm = ClasificadorEstructuraHMM(numero_estados_ocultos=3)
            hmm.entrenar_modelos(registros)
            genero_predicho, probabilidades = hmm.predecir_genero(sim_bat, sim_voz, sim_bajo, sim_otros)

        nombre_pista = os.path.basename(ruta_mp3)
        self.db.guardar_registro(
            nombre_pista=nombre_pista,
            bpm=float(bpm),
            golpes=int(len(tiempos)),
            cadena_bateria=sim_bat,
            cadena_voz=sim_voz,
            cadena_bajo=sim_bajo,
            cadena_otros=sim_otros,
            genero=genero_predicho
        )

        return {
            "nombre_pista": nombre_pista,
            "bpm": float(bpm),
            "golpes": len(tiempos),
            "stems": rutas_stems,
            "sintaxis": {
                "bateria": sim_bat,
                "voz": sim_voz,
                "bajo": sim_bajo,
                "otros": sim_otros
            },
            "genero_predicho": genero_predicho,
            "probabilidades_hmm": probabilidades
        }