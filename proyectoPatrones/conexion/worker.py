import os 
from PyQt6.QtCore import QThread, pyqtSignal
from modulos.separador import MotorSeparacion  
from modulos.analizador import AnalizadorPercusion
from modulos.bajo import AnalizadorBajo
from modulos.voz import AnalizadorVoz
from modulos.otros import AnalizadorOtros 
from modulos.simbolico import PreprocesadorSimbolico
from modulos.modeloHMM import ClasificadorEstructuraHMM

# -*- coding: utf-8 -*-

class WorkerProcesamiento(QThread):
	terminado = pyqtSignal(str)
	error = pyqtSignal(str)


	def __init__(self, ruta_archivo, db):
		super().__init__()
		self.ruta_archivo = ruta_archivo
		self.db = db

	def run(self):
		try:
			separador = MotorSeparacion(modelo="htdemucs")
			rutas_stems = separador.procesar_pista(self.ruta_archivo)

			if not rutas_stems:
				self.error.emit("El motor de separación no pudo generar los stems.")
				return

			analizador_bat = AnalizadorPercusion(rutas_stems["bateria"])
			bpm, tiempos = analizador_bat.extraer_bpm_y_golpes()
			total_golpes = len(tiempos)
			seq_bat = analizador_bat.extraer_secuencia_temporal()

			seq_bajo = AnalizadorBajo(rutas_stems["bajo"]).extraer_secuencia_temporal()
			seq_voz = AnalizadorVoz(rutas_stems["voz"]).extraer_secuencia_temporal()
			seq_otros = AnalizadorOtros(rutas_stems["otros"]).extraer_secuencia_temporal()

			sim_bat = PreprocesadorSimbolico().transformar_a_simbolos(seq_bat) or "A"
			sim_voz = PreprocesadorSimbolico().transformar_a_simbolos(seq_voz) or "A"
			sim_bajo = PreprocesadorSimbolico().transformar_a_simbolos(seq_bajo) or "A"
			sim_otros = PreprocesadorSimbolico().transformar_a_simbolos(seq_otros) or "A"

			registros = self.db.entrenamiento()
			hmm = ClasificadorEstructuraHMM()
			if registros:
				hmm.entrenar_modelos(registros)
				genero_predicho, _ = hmm.predecir_genero(sim_bat, sim_voz,sim_bajo,sim_otros)

			else:
				genero_predicho = "Entrenamiento"

			nombre_pista = os.path.basename(self.ruta_archivo)

			self.db.guardar_registro(
				nombre_pista=nombre_pista,
				bpm= float(bpm),
				golpes = int(total_golpes),
				cadena_bateria = sim_bat,
				cadena_voz = sim_voz,
				cadena_bajo = sim_bajo,
				cadena_otros = sim_otros,
				genero = genero_predicho
			)

			self.terminado.emit(nombre_pista)

		except Exception as e:
			print(f" Error crítico en el worker independiente: {e}")
			self.error.emit(str(e))
			
