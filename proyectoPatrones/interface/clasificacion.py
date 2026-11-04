import os 
import sqlite3
from PyQt6.QtWidgets import (
	QWidget,QVBoxLayout,QHBoxLayout,QLabel,QListWidget,QLineEdit,QScrollArea,QFrame,QGridLayout
)

from PyQt6.QtCore import Qt


from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.figure import Figure

from modulos.database import GestorBaseDatos

class TarjetaGrafica(QFrame):
	def __init__(self,titulo_tarjeta, figura):
		super().__init__()
		self.titulo_tarjeta = titulo_tarjeta
		self.figura = figura
		self._inicializar_ui()

	def _inicializar_ui(self):
		self.setStyleSheet("""
			TarjetaGrafica {
				background-color: #181818;
				border: 1px solid #2a2a2a;
				border-radius: 8px;
				margin: 6px;
			}
		""")

		layout = QVBoxLayout()
		layout.setContentsMargins (15,15,15,15)

		self.lbl_titulo= QLabel(self.titulo_tarjeta)
		self.lbl_titulo.setStyleSheet("""
			color:#ffffff;
			font-weight: bold;
			font-size: 14px;
			border: none;
		""")

		layout.addWidget(self.lbl_titulo)

		if self.figura:
			self.canvas= FigureCanvas(self.figura)
			self.canvas.setStyleSheet("background-color: transparent;")
			layout.addWidget(self.canvas)

		self.setLayout(layout)

class ClasificacionHMM(QWidget):
	def __init__(self):
		super().__init__()
		self.pistas_guardadas = []
		self.db = GestorBaseDatos()
		self._inicializar_ui()
		self.cargar_historial_db()


	def _inicializar_ui(self):
		layout_principal = QHBoxLayout()
		layout_principal.setContentsMargins(20,20,20,20)
		layout_principal.setSpacing(20)

		panel_izquierdo = QVBoxLayout()
		titulo_izq = QLabel("Historial de Clasificación")
		titulo_izq.setStyleSheet("""
			color: #ffffff;
			font-weight: bold ;
			font-size: 14px ;
		""")

		panel_izquierdo.addWidget(titulo_izq)
		self.input_buscar_clas = QLineEdit()
		self.input_buscar_clas.setPlaceholderText ("Buscar pista analizada...")
		self.input_buscar_clas.textChanged.connect(self.filtrar_historial)
		self.input_buscar_clas.setStyleSheet("""
			QLineEdit {
				background-color: #2b2b2b;
				color:#ffffff;
				border:1px solid #3d3d3d;
				border-radius: 6px;
				padding:6px 10px;
				font-size:12px;
				
			} 
			QLineEdit::focus{
				border: 1px solid #1db954;
			}

		""")
		panel_izquierdo.addWidget(self.input_buscar_clas)


		self.listas_pistas = QListWidget()
		self.listas_pistas.setStyleSheet("""
			QListWidget{
				background-color: #121212;
				color: #e0e0e0;
				border: 1px solid #2a2a2a;
				border-radius: 8px;
				padding: 5px;
			}
		""")
		self.listas_pistas.currentTextChanged.connect(self.cargar_analisis_pista)
		panel_izquierdo.addWidget(self.listas_pistas)

		container_izq = QWidget()
		container_izq.setLayout(panel_izquierdo)
		container_izq.setFixedWidth(250)
		layout_principal.addWidget(container_izq)

		panel_derecho = QVBoxLayout()
		titulo_der = QLabel("Clasificación de Estructura y HMM")
		titulo_der.setStyleSheet("""
			color: #ffffff;
			font-weight: bold;
			font-size: 18px;
		""")
		panel_derecho.addWidget(titulo_der)

		self.scroll_area = QScrollArea()
		self.scroll_area.setWidgetResizable(True)
		self.scroll_area.setStyleSheet("""
			QScrollArea {
				background-color: transparent;
				border: none;
			}
		""")

		self.contenedor_tarjetas = QWidget()
		self.grid_tarjetas= QGridLayout(self.contenedor_tarjetas)
		self.grid_tarjetas.setContentsMargins(0,0,0,0)
		self.grid_tarjetas.setSpacing(15)

		self.scroll_area.setWidget(self.contenedor_tarjetas)
		panel_derecho.addWidget(self.scroll_area)

		container_der= QWidget()
		container_der.setLayout(panel_derecho)
		layout_principal.addWidget(container_der)

		self.setLayout(layout_principal)

		self.mostrar_tarjeta_bienvenida()


	def mostrar_tarjeta_bienvenida(self):
		fig = Figure(figsize=(5,3))
		ax = fig.add_subplot(111)
		ax.set_facecolor('#181818')
		fig.patch.set_facecolor('#181818')
		ax.text(0.5,0.5,"eleccione una pista del historial\npara ver el análisis HMM y gráficas",
			color='#a0a0a0', horizontalalignment= 'center', verticalalignment='center',fontsize=12)
		ax.axis('off')

		tarjeta = TarjetaGrafica("Estado del Sistema",fig)
		self.grid_tarjetas.addWidget(tarjeta, 0, 0)

	def cargar_historial_db (self):
		try:
			with sqlite3.connect(self.db.ruta_db) as conexion:
				cursor = conexion.cursor()
				cursor.execute ("SELECT nombre_archivo FROM pistas_entrenamiento")
				registros = cursor.fetchall()

				self.pistas_guardadas = [reg[0] for reg in registros]
				self.actualizar_lista_visual(self.pistas_guardadas)

		except Exception as e:
			print(f"Error al cargar historial de cllasificacion: {e}")
			
			
	def cargar_pista_seleccionada(self, nombre_pista):
		if nombre_pista not in self.pistas_guardadas:
			self.pistas_guardadas.append(nombre_pista)
		self.actualizar_lista_visual(self.pistas_guardadas)
		
		items = self.listas_pistas.findItems(nombre_pista, Qt.MatchFlag.MatchExactly if hasattr (Qt, 'MatchFlag')else 0)		
		if items:
			self.listas_pistas.setCurrentItem(items[0])

	def cargar_analisis_pista(self, nombre_pista):
		if not nombre_pista:
			return

		print(f"Cargar analisis HMM y metricas para: {nombre_pista}")

		try:
			with sqlite3.connect(self.db.ruta_db) as conexion:
				cursor = conexion.cursor()
				cursor.execute("""
					SELECT bpm, total_golpes, sintaxis_bateria, sintaxis_voz, sintaxis_bajo, sintaxis_otros, genero 
                    FROM pistas_entrenamiento WHERE nombre_archivo = ?
				""", (nombre_pista,))

				resultado = cursor.fetchone()

				if resultado:
					bpm, golpes, bat, voz, bajo, otros, genero = resultado
					self.renderizar_tarjetas_analisis(nombre_pista, bpm, golpes, bat, voz, bajo, otros, genero)

		except Exception as e:
			print(f"Error consultando detalles de la pista: {e}")

	def renderizar_tarjetas_analisis (self,pista, bpm, golpes, bat, voz, bajo, otros, genero):
		while self.grid_tarjetas.count():
			item = self.grid_tarjetas.takeAt(0)
			widget = item.widget()
			if widget:
				widget.deleteLater()

			fig_resumen = Figure(figsize=  (5,2.5))
			ax1= fig_resumen.add_subplot(111)
			ax1.set_facecolor("#181818")
			fig_resumen.patch.set_facecolor('#181818')

			texto_resumen = (
				f"Pista: {pista}\n"
				f"Género Predicho (HMM): {genero}\n"
				f"BPM: {bpm:.1f} | Golpes Totales: {golpes}"
			)

			ax1.text(0.05,0.5, texto_resumen, color='#ffffff', fontsize=11, verticalalignment='center')
			self.grid_tarjetas.addWidget(TarjetaGrafica("Resumen de Clasificación HMM", fig_resumen), 0,0)

			fig_sintaxis = Figure(figsize=(5, 2.5))
			ax2= fig_sintaxis.add_subplot(111)
			ax2.set_facecolor('#181818')
			fig_sintaxis.patch.set_facecolor('#181818')

			texto_sintaxis = (
				f"Bateria [A-E]: {bat}\n"
				f"Voz [X-Z]: {voz}\n"
				f"Bajo [B1-B3]: {bajo}\n"
				f"Otros [01-03]: {otros}"
			)

			ax2.text(0.05,0.5, texto_sintaxis, color='#1db954', fontsize=11, fontweight='bold', verticalalignment='center')
			ax2.axis('off')
			self.grid_tarjetas.addWidget(TarjetaGrafica("Cadenas Simbólicas por Stem", fig_sintaxis),0,1)
			fig_grafica = Figure(figsize =(5,3))
			ax3 = fig_grafica.add_subplot(111)
			ax3.set_facecolor('#181818')
			fig_grafica.patch.set_facecolor('#181818')

			stems_nombre = ['Batería','Voz','Bajo','Otros']

			longitudes = [len(bat.split('-')),len(voz.split('-')),len(bajo.split('-')),len(otros.split('-'))]

			ax3.bar(stems_nombre, longitudes, color ='#1db954', alpha= 0.8)
			ax3.set_title("Densidad de Ventanas por Stem", color= '#ffffff', fontsize=10)
			ax3.tick_params(colors='#3d3d3d')
			ax3.spines['bottom'].set_color('#3d3d3d')
			ax3.spines['left'].set_color('#3d3d3d')
			ax3.spines['top'].set_visible(False)
			ax3.spines['right'].set_visible(False)

			self.grid_tarjetas.addWidget(TarjetaGrafica ("Métricas Estructurales de Stems", fig_grafica), 1,0,1,2)

	def filtrar_historial(self, texto):
		texto = texto.lower()
		filtradas = [p for p in self.pistas_guardadas if texto in p.lower()]
		self.actualizar_lista_visual(filtradas)

	def actualizar_lista_visual(self,lista):
		self.listas_pistas.clear()
		for pista in lista:
			self.listas_pistas.addItem(pista)

				
