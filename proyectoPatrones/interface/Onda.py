from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QPen
import random

class Onda(QWidget):
	def __init__(self, parent=None):
		super().__init__(parent)
		self.setFixedHeight(30)
		self.barras = [random.randint(6,26) for _ in range(60)]

	def paintEvent(self,event):
		painter = QPainter(self)
		painter.setRenderHint(QPainter.RenderHint.Antialiasing)

		pen = QPen(QColor("#1db954"))
		pen.setWidth(2)
		painter.setPen(pen)

		width = self.width()
		height = self.height()

		ancho_barra = 6
		num_bars = max(5, width // ancho_barra)
		barras_dinamicas = [self.barras[i % len(self.barras)] for i in range(num_bars) ]
		bar_width = width / len(barras_dinamicas)

		for i, altura in enumerate (self.barras):
			x = int(i*bar_width + bar_width / 2)
			y1 = int((height - altura)/2)
			y2 = int ((height + altura)/2)
			painter.drawLine(x, y1, x, y2 )

	def resizeEvent(self,event):
		super().resizeEvent(event)
		self.update()

		
