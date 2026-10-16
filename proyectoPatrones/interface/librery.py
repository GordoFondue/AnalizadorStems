import os
import sqlite3
from PyQt6.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
	QMessageBox
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
		
		titulo = QLabel("Libreria")
		titulo.setStyleSheet(" font-size: 14px; font-weight: bold; color: #2c3e50;")
		layout_principal.addWidget(titulo)

		layout_busqueda = QHBoxLayout()
		self.input_buscar = QLineEdit()
		self.input_buscar.setPlaceholderText("Nombre del Archivo")
		self.input_buscar.textChanged.connect(self.filtrar_tabla)
		layout_busqueda.addWidget(self.input_buscar)

		self.btn_recargar = QPushButton ("Atualizar")
		self.btn_recargar.clicked.connect(self.cargar_datos_tabla)
		layout_busqueda.addWidget(self.btn_recargar)

		layout_principal.addLayout(layout_busqueda)

		self.tabla = QTableWidget()
		self.tabla.setColumnCount(6)
		self.tabla.setHorizontalHeaderLabels([
			"No.","Nombre","BPM","Golpes","Sintaxis Bateria","Genero"
		])
		
		self.tabla.horizontalHeader().setStretchLastSection(True)
		layout_principal.addWidget (self.tabla)
		
		self.setLayout(layout_principal)

	def cargar_datos_tabla (self,filtro=""):
		try:
			conexion = self.db.ruta_db
			with sqlite3.connect(conexion) as conn:
				cursor = conn.cursor()
				if filtro:
					query = """
						SELECT id,nombre_archivo,bpm,total_golpes,sintaxis_bateria,genero
						FROM pista_entrenamiento
						WHERE nombre_archivo LIKE ? OR genero LIKE ?
						"""
					cursor.execute(query,(f"%{filtro}",f"%{filtro}"))
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
