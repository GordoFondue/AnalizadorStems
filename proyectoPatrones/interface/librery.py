import os
import sqlite3
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
	QMessageBox, QHeaderView
)

from PyQt6.QtCore import Qt
from modulos.database import GestorBaseDatos

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
		
		titulo = QLabel("Libreria")
		titulo.setStyleSheet(" font-size: 20px; font-weight: bold; color: #ffffff;")
		layout_principal.addWidget(titulo)

		sub_titulo = QLabel("Bienvenido al sistema de analizador musical")
		sub_titulo.setStyleSheet("""
			font-size: 12px;
			color: #a0a0a0;
		""")

		layout_principal.addWidget(sub_titulo)

		layout_busqueda = QHBoxLayout()
		
		self.input_buscar = QLineEdit()
		self.input_buscar.setPlaceholderText("Buscar canciones, artistas o generos!")
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

		layout_busqueda.addWidget(self.input_buscar)

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
		layout_busqueda.addWidget(self.btn_recargar)

		layout_principal.addLayout(layout_busqueda)

		self.tabla = QTableWidget()
		self.tabla.setColumnCount(6)
		self.tabla.setHorizontalHeaderLabels([
			"No.","Nombre","BPM","Golpes","Sintaxis Bateria","Genero"
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
		self.tabla.setColumnWidth(2,70)
		header.setSectionResizeMode(3,QHeaderView.ResizeMode.Fixed)
		self.tabla.setColumnWidth(3,70)
		header.setSectionResizeMode(4,QHeaderView.ResizeMode.ResizeToContents)
		header.setSectionResizeMode(5,QHeaderView.ResizeMode.ResizeToContents)

		self.tabla.verticalHeader().setVisible(False)
		layout_principal.addWidget(self.tabla)

		self.setLayout(layout_principal)

		
	def cargar_datos_tabla (self,filtro=""):
		try:
			conexion = self.db.ruta_db
			with sqlite3.connect(conexion) as conn:
				cursor = conn.cursor()
				if filtro:
					query = """
						SELECT id,nombre_archivo,bpm,total_golpes,sintaxis_bateria,genero
						FROM pistas_entrenamiento
						WHERE nombre_archivo LIKE ? OR genero LIKE ?
						"""
					cursor.execute(query,(f"%{filtro}%",f"%{filtro}%"))
				else: 
					query = """
						SELECT id,nombre_archivo, bpm, total_golpes, sintaxis_bateria,genero
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
			print (f"Error al caragar datos: {e}")

	def filtrar_tabla (self,texto):
		self.cargar_datos_tabla(filtro = texto)
