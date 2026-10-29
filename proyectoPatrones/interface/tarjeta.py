from PyQt6.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QPushButton, QLabel, QSlider
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt

from interface.Onda import Onda

class TarjetaStem(QFrame):
	def __init__(self,nombre):
		super().__init__()
		self.nombre_stem = nombre

		self.player = QMediaPlayer()
		self.audio_output = QAudioOutput()
		self.player.setAudioOutput(self.audio_output)
		self.audio_output.setVolume(1.0)

		self.is_seeking = False

		self._inicializar_ui()

	def _inicializar_ui(self):
		self.setStyleSheet("""
			TarjetaStem {
				background-color: #181818;
				border:1px solid #2a2a2a;
				border-radius: 8px;
				margin: 4px 0px;
			}
		""")

		layout = QHBoxLayout()
		layout.setContentsMargins(15,10,15,10)

		self.btn_play = QPushButton("▶")
		self.btn_play.setFixedSize(32,32)
		self.btn_play.setStyleSheet("""
			QPushButton {
				background-color: #1db954;
				color: #ffffff;
				border-radius:16px;
				font-size: 13px;
				font-weight: bold;
				border: none;
			}
			QPushButton::hover{background-color: #1ed760;}
		""")
		self.btn_play.clicked.connect(self.reproducir_audio)
		layout.addWidget(self.btn_play)

		self.btn_pausa = QPushButton("⏸")
		self.btn_pausa.setFixedSize(32,32)
		self.btn_pausa.setStyleSheet("""
			QPushButton {
				background-color: #2b2b2b;
				color: #ffffff;
				border-radius:16px;
				font-size: 13px;
				font-weight: bold;
				border: none;
			}
			QPushButton::hover{background-color: #3d3d3d;}
		""")
		self.btn_pausa.clicked.connect(self.pausar_audio)
		layout.addWidget(self.btn_pausa)

		info_layout = QVBoxLayout()
		self.lbl_nombre = QLabel(self.nombre_stem.upper())
		self.lbl_nombre.setStyleSheet("""
			color:#ffffff;
			font-weight:bold;
			font-size: 13px;
			border: none;
		""")

		self.onda = Onda()

		info_layout.addWidget(self.lbl_nombre)
		info_layout.addWidget(self.onda)

		layout_progreso = QHBoxLayout()
		layout.addLayout(info_layout)

		self.lbl_tiempo = QLabel("0:00 / 0:00")
		self.lbl_tiempo.setStyleSheet("""
			color:#a0a0a0;
			font-size: 12px;
			border:none;
		""")

		self.slider_progreso = QSlider(Qt.Orientation.Horizontal)
		self.slider_progreso.setRange(0,0)
		self.slider_progreso.setStyleSheet("""
			QSlider::groove:horizontal {
				border: none;
				height: 4px;
				background: #3d3d3d;
				border-radius: 2px;
			}
			QSlider::sub-page:horizontal{
				background: #1db954;
				border-radius: 2px;
			}
			QSlider::handle:horizontal{
				background: #ffffff;
				border:none;
				width:10px;
				height:10px;
				margin:-3px 0;
				border-radius: 5px;
			}
		""")

		self.slider_progreso.sliderPressed.connect(lambda: setattr(self, 'is_seeking',True))
		self.slider_progreso.sliderReleased.connect(self.saltar_posicion)

		layout_progreso.addWidget(self.slider_progreso)
		layout_progreso.addWidget(self.lbl_tiempo)

		info_layout.addLayout(layout_progreso)

		self.setLayout(layout)

		self.player.positionChanged.connect(self.actualizar_posicion_reproductor)
		self.player.durationChanged.connect(self.actualizar_duracion_total)
		

	def cargar_archivo_stem(self, ruta_archivo):
		self.player.setSource(QUrl.fromLocalFile(ruta_archivo))

	def reproducir_audio(self):
		if self.player.source().isEmpty():
			print(f"[{self.nombre_stem}] No hay archivo de audio cargado todavía.")
			return
		self.player.play()
		print(f"Reproduciendo: {self.nombre_stem}")

	def pausar_audio(self):
		self.player.pause()
		print(f"Pausado: {self.nombre_stem}")
		
	def actualizar_duracion_total(self,duracion):
		self.slider_progreso.setRange(0,duracion)

	def actualizar_posicion_reproductor (self, posicion):
		if not self.is_seeking:
			self.slider_progreso.setValue(posicion)

		tiempo_actual = self.formatear_tiempo(posicion)
		duracion_total = self.formatear_tiempo(self.player.duration())
		self.lbl_tiempo.setText(f"{tiempo_actual} / {duracion_total}")

	def saltar_posicion(self):
		nueva_posicion = self.slider_progreso.value()
		self.player.setPosition(nueva_posicion)
		self.is_seeking = False

	def formatear_tiempo(self,ms):
		segundos = int(ms/1000)
		minutos = segundos //60
		segundos = segundos % 60
		return f"{minutos}:{segundos:02d}"
