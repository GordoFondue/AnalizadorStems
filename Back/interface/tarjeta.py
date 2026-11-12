import os
from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput


class TarjetaStem(QFrame):
    def __init__(self, nombre_stem):
        super().__init__()
        self.nombre_stem = nombre_stem
        self._arrastrando_slider = False
        self._volumen_previo = 80
        self._inicializar_ui()

    def _inicializar_ui(self):
        self.setStyleSheet("""
            TarjetaStem {
                background-color: #181818;
                border: 1px solid #2a2a2a;
                border-radius: 10px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(8)

        # Fila superior: Título del stem + controles de volumen individual
        fila_superior = QHBoxLayout()

        self.lbl_nombre = QLabel(self.nombre_stem)
        self.lbl_nombre.setStyleSheet(
            "color: #ffffff; font-weight: bold; font-size: 14px; border: none;"
        )
        fila_superior.addWidget(self.lbl_nombre)
        fila_superior.addStretch()

        self.btn_mute = QPushButton("🔊")
        self.btn_mute.setFixedSize(28, 28)
        self.btn_mute.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mute.setStyleSheet("""
            QPushButton {
                background-color: #282828;
                color: #ffffff;
                border-radius: 14px;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #383838; }
        """)
        self.btn_mute.clicked.connect(self.toggle_mute)
        fila_superior.addWidget(self.btn_mute)

        self.slider_volumen = QSlider(Qt.Orientation.Horizontal)
        self.slider_volumen.setRange(0, 100)
        self.slider_volumen.setValue(80)
        self.slider_volumen.setFixedWidth(110)
        self.slider_volumen.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: #3d3d3d;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #1db954;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        self.slider_volumen.valueChanged.connect(self.cambiar_volumen)
        fila_superior.addWidget(self.slider_volumen)

        self.lbl_volumen = QLabel("80%")
        self.lbl_volumen.setFixedWidth(36)
        self.lbl_volumen.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_volumen.setStyleSheet("color: #a0a0a0; font-size: 12px; border: none;")
        fila_superior.addWidget(self.lbl_volumen)

        layout.addLayout(fila_superior)

        # Fila inferior: Botón Play/Pause individual + barra de tiempo
        fila_reproduccion = QHBoxLayout()
        fila_reproduccion.setSpacing(10)

        self.btn_play = QPushButton("▶")
        self.btn_play.setFixedSize(34, 34)
        self.btn_play.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_play.setStyleSheet("""
            QPushButton {
                background-color: #1db954;
                color: #ffffff;
                border-radius: 17px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover { background-color: #1ed760; }
        """)
        self.btn_play.clicked.connect(self.toggle_play)
        fila_reproduccion.addWidget(self.btn_play)

        self.lbl_tiempo_actual = QLabel("00:00")
        self.lbl_tiempo_actual.setStyleSheet("color: #a0a0a0; font-size: 11px; border: none;")
        fila_reproduccion.addWidget(self.lbl_tiempo_actual)

        self.slider_tiempo = QSlider(Qt.Orientation.Horizontal)
        self.slider_tiempo.setRange(0, 0)
        self.slider_tiempo.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 5px;
                background: #3d3d3d;
                border-radius: 2px;
            }
            QSlider::sub-page:horizontal {
                background: #1db954;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ffffff;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
        """)
        self.slider_tiempo.sliderPressed.connect(self._inicio_arrastre)
        self.slider_tiempo.sliderReleased.connect(self._fin_arrastre)
        self.slider_tiempo.sliderMoved.connect(self._mover_posicion)
        fila_reproduccion.addWidget(self.slider_tiempo)

        self.lbl_duracion = QLabel("00:00")
        self.lbl_duracion.setStyleSheet("color: #a0a0a0; font-size: 11px; border: none;")
        fila_reproduccion.addWidget(self.lbl_duracion)

        layout.addLayout(fila_reproduccion)

        # Reproductor y salida de audio independiente
        self.player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.8)

        self.player.positionChanged.connect(self._actualizar_posicion)
        self.player.durationChanged.connect(self._actualizar_duracion)
        self.player.playbackStateChanged.connect(self._actualizar_boton_play)

    def cargar_archivo_stem(self, ruta_archivo):
        self.player.stop()
        self.player.setSource(QUrl.fromLocalFile(os.path.abspath(ruta_archivo)))

    def toggle_play(self):
        if self.player.source().isEmpty():
            return
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause()
        else:
            self.player.play()

    def cambiar_volumen(self, valor):
        self.audio_output.setVolume(valor / 100.0)
        self.lbl_volumen.setText(f"{valor}%")
        self.btn_mute.setText("🔇" if valor == 0 else "🔊")

    def toggle_mute(self):
        actual = self.slider_volumen.value()
        if actual > 0:
            self._volumen_previo = actual
            self.slider_volumen.setValue(0)
        else:
            self.slider_volumen.setValue(self._volumen_previo or 80)

    def _inicio_arrastre(self):
        self._arrastrando_slider = True

    def _fin_arrastre(self):
        self._arrastrando_slider = False
        self.player.setPosition(self.slider_tiempo.value())

    def _mover_posicion(self, posicion):
        self.lbl_tiempo_actual.setText(self._formatear_ms(posicion))

    def _actualizar_posicion(self, posicion):
        if not self._arrastrando_slider:
            self.slider_tiempo.setValue(posicion)
            self.lbl_tiempo_actual.setText(self._formatear_ms(posicion))

    def _actualizar_duracion(self, duracion):
        self.slider_tiempo.setRange(0, duracion)
        self.lbl_duracion.setText(self._formatear_ms(duracion))

    def _actualizar_boton_play(self, estado):
        if estado == QMediaPlayer.PlaybackState.PlayingState:
            self.btn_play.setText("⏸")
        else:
            self.btn_play.setText("▶")

    @staticmethod
    def _formatear_ms(ms):
        segundos = max(0, ms // 1000)
        minutos = segundos // 60
        resto = segundos % 60
        return f"{minutos:02d}:{resto:02d}"