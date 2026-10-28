from PyQt6.QtWidgets import QMessageBox

class GestorDiagnostico:
	@staticmethod
	def mostrar_error (parent,titulo, mensaje):
		QMessageBox.critical(
			parent,
			f"Error de Diagnostico: {titulo}",
			mensaje,
			QMessageBox.StandardButton.Ok
		)

	@staticmethod
	def mostrar_advertencia (parent,titulo, mensaje):
		QMessageBox.warning (
		parent,
		f"Advertencia: {titulo}",
		mensaje,
		QMessageBox.StandardButton.Ok
	)

	@staticmethod
	def mostrar_exito (parent,titulo, mensaje):
		QMessageBox.information(
			parent,
			titulo,
			mensaje,
			QMessageBox.StandardButton.Ok
		)
