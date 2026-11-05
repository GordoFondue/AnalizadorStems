from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QInputDialog

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
    
    @staticmethod
    def solicitar_nuevo_genero(parent, nombre_pista,genero_actual=""):
        nuevo_genero, ok = QInputDialog.getText(
            parent,
            "Editar Género Musical",
            f"Modificar género para: \n {nombre_pista}",
            text= genero_actual
        )
        if ok and nuevo_genero.strip():
            return nuevo_genero.strip()
        return None
