import os
import sqlite3
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
	QMessageBox, QHeaderView, QFileDialog,QProgressBar
)

from PyQt6.QtCore import Qt, QTimer
from modulos.database import GestorBaseDatos
from conexion.worker import WorkerProcesamiento
from ventanas.dialogos import GestorDiagnostico
from acciones.click import GestorMenuContextual

class Librery (QWidget):

	def __init__ (self):
		super().__init__()

		self.db =GestorBaseDatos()
		self._inicializar_ui()
		self.cargar_datos_tabla()

	def _inicializar_ui(self):
		layout_principal = QVBoxLayout()
		layout_principal.setContentsMargins(20,20,20,20)
		layout_principal.setSpacing(15)
		
		titulo = QLabel("Librería")
		titulo.setStyleSheet(" font-size: 20px; font-weight: bold; color: #ffffff;")
		layout_principal.addWidget(titulo)

		sub_titulo = QLabel("Bienvenido al sistema de analizador musical")
		sub_titulo.setStyleSheet("""
			font-size: 12px;
			color: #a0a0a0;
		""")

		layout_principal.addWidget(sub_titulo)

		layout_acciones = QHBoxLayout()

		self.btn_seleccionar = QPushButton ("Seleccionar archivos")
		self.btn_seleccionar.setStyleSheet("""
			QPushButton {
				background-color: #1db954;
				color: #ffffff;
				border-radius: 6px;
				padding: 8px 16px;
				font-weight: bold;
			}
			QPushButton:hover {
				background-color: #1ed760;
			}
		"""
		)

		self.btn_seleccionar.clicked.connect(self.abrir_explorador_archivos)
		layout_acciones.addWidget(self.btn_seleccionar)
		
		
		self.input_buscar = QLineEdit()
		self.input_buscar.setPlaceholderText("Buscar canciones, artistas o géneros...")
		self.input_buscar.textChanged.connect(self.filtrar_tabla)
		self.input_buscar.setStyleSheet("""
			QLineEdit {
				background-color: #2b2b2b;
				color: #ffffff;
				border: 1px solid #3d3d3d;
				border-radius: 6px;
				padding: 8px 12px;
				font-size: 13px;
			}
			QLineEdit:focus {
				border: 1px solid #1db954;
			}
		""")

		layout_acciones.addWidget(self.input_buscar)

		self.btn_recargar = QPushButton ("Actualizar")
		self.btn_recargar.setStyleSheet("""
			QPushButton {
				background-color: #2b2b2b;
				color: #ffffff;
				border: 1px solid #3d3d3d;
				border-radius: 6px;
				padding: 8px 16px;
				font-weight: bold;
			}
			QPushButton:hover {
				background-color: #3d3d3d;
			}
		"""
		)
		
		self.btn_recargar.clicked.connect(self.cargar_datos_tabla)
		layout_acciones.addWidget(self.btn_recargar)
		
		layout_principal.addLayout(layout_acciones)

		self.barra_progreso = QProgressBar()
		
		self.barra_progreso.setRange(0,100)
		self.barra_progreso.setValue(0)
		self.barra_progreso.setVisible(False)
		self.barra_progreso.setStyleSheet("""
			QProgressBar{
				background-color: #2b2b2b;
				border: 1px solid #3d3d3d;
				border-radius: 4px;
				height: 8px;
				text-align: center;
			}
			QProgressBar::chunk {
				background-color: #1db954;
				border-radius: 4px;
			}
		""")

		layout_principal.addWidget(self.barra_progreso)

		self.timer_progreso = QTimer(self)
		self.timer_progreso.timeout.connect(self.actualizar_progreso_visual)

		self.tabla = QTableWidget()
		self.tabla.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.tabla.customContextMenuRequested.connect(self.mostrar_menu_contextual)
		self.tabla.setColumnCount(4)
		self.tabla.setHorizontalHeaderLabels([
			"No.", "Nombre", "BPM", "Género"
		])

		self.tabla.setStyleSheet("""
			QTableWidget {
				background-color: #121212;
				color: #e0e0e0e0;
				gridline-color: #2a2a2a;
				border: 1px solid #2a2a2a;
				border-radius: 8px;
			}
			QHeaderView::section {
				background-color:#181818 ;
				color: #a0a0a0a0;
				padding: 8px;
				border: none;
				border-bottom: 1px solid #2a2a2a;
				font-weight: bold;
			}
			QTableWidget :: item{
				padding: 6px;
				border-bottom: 1px solid #1a1a1a;
			} 
			QTableWidget::item:selected {
				background-color: #282828;
				color: #ffffff;
			}
		""")
		

		header = self.tabla.horizontalHeader()
		header.setSectionResizeMode(0,QHeaderView.ResizeMode.Fixed)
		self.tabla.setColumnWidth(0,50)
		header.setSectionResizeMode(1,QHeaderView.ResizeMode.Stretch)
		header.setSectionResizeMode(2,QHeaderView.ResizeMode.Fixed)
		self.tabla.setColumnWidth(2,80)
		header.setSectionResizeMode(3,QHeaderView.ResizeMode.ResizeToContents)

		self.tabla.verticalHeader().setVisible(False)
		layout_principal.addWidget(self.tabla)

		self.setLayout(layout_principal)

	def abrir_explorador_archivos(self):
		archivo_ruta, _=QFileDialog.getOpenFileName(
			self, 
			"Seleccionar pista de audio para analizar",
			"",
			"Archivos de Audio (*.mp3 *.wav *.flac);;Todos los archivos (*.*)"
		)

		if archivo_ruta:
			self.btn_seleccionar.setEnabled(False)
			self.btn_seleccionar.setText("Analizando...")
			self.barra_progreso.setValue(0)
			self.barra_progreso.setVisible(True)

			self.worker = WorkerProcesamiento(archivo_ruta,self.db)
			self.worker.progreso.connect(self.barra_progreso.setValue)
			self.worker.terminado.connect(self.proceso_finalizado)
			self.worker.error.connect(self.proceso_error)
			self.worker.start()
			

	def proceso_finalizado(self, nombre_pista):
		self.btn_seleccionar.setEnabled(True)
		self.btn_seleccionar.setText("Seleccionar archivos")
		self.barra_progreso.setVisible(False)
		self.cargar_datos_tabla()

		GestorDiagnostico.mostrar_exito(
			self,
			"Analisis Exitosa",
			f"La pista {nombre_pista} fue procesada y guardada correctamente"
		)

	def proceso_error(self,mensaje_error):
		self.btn_seleccionar.setEnabled(True)
		self.btn_seleccionar.setText("Seleccionar archivos")
		self.cargar_datos_tabla()
		GestorDiagnostico.mostrar_error(
			self,
			"Fallo en Procesamiento de Audio",
			f"Ocurrio un error al procesar el archivo: \n {mensaje_error}"
		)

	def actualizar_progreso_visual(self):
		valor_actual = self.barra_progreso.value()
		if valor_actual < 95:
			self.barra_progreso.setValue(valor_actual + 5)
			
	def cargar_datos_tabla (self,filtro=""):
		try:
			conexion = self.db.ruta_db
			with sqlite3.connect(conexion) as conn:
				cursor = conn.cursor()
				if filtro:
					query = """
						SELECT id,nombre_archivo,bpm,genero
						FROM pistas_entrenamiento
						WHERE nombre_archivo LIKE ? OR genero LIKE ?
						"""
					cursor.execute(query,(f"%{filtro}%",f"%{filtro}%"))
				else: 
					query = """
						SELECT id,nombre_archivo, bpm,genero
						FROM pistas_entrenamiento
						"""
					cursor.execute(query)

				registros = cursor.fetchall()

			self.tabla.setRowCount(len(registros))
			for fila_idx, fila_data in enumerate (registros):
				for col_idx, valor  in enumerate (fila_data):
					item = QTableWidgetItem(str(valor))
					item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)
					self.tabla.setItem(fila_idx,col_idx, item)
		except Exception as e:
			print (f"Error al cargar datos: {e}")

	def filtrar_tabla (self,texto):
		self.cargar_datos_tabla(filtro = texto)

	def mostrar_menu_contextual(self,posicion):
		punto = self.tabla.mapToGlobal(posicion)
		fila_seleccionada = self.tabla.currentRow()

		if fila_seleccionada >= 0:
			item_pista = self.tabla.item(fila_seleccionada, 1)
			if item_pista:
				nombre_pista = item_pista.text()

				menu = GestorMenuContextual.crear_menu_libreria(
					self,
					nombre_pista,
					callback_ver_separacion = self.ir_a_pestana_separacion
				)
				menu.exec(punto)


	def ir_a_pestana_separacion(self, nombre_pista):
		ventana_principal = self.window()
		if hasattr(ventana_principal,"tabs"):
			ventana_principal.tabs.setCurrentIndex(1)
			ventana_principal.pestana_separacion.cargar_pista_seleccionada(nombre_pista)
