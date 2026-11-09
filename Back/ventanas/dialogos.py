from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QInputDialog, QLineEdit

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

    @staticmethod
    def solicitar_contrasena_admin(parent):
        """Devuelve la contraseña escrita, o None si el usuario cancela."""
        texto, ok = QInputDialog.getText(
            parent,
            "Acceso de administrador",
            "Ingresa la contraseña de administrador:",
            QLineEdit.EchoMode.Password
        )
        return texto if ok else None


    @staticmethod
    def solicitar_nueva_contrasena_admin(parent):
        """Pide crear la contraseña de administrador (dos veces). Devuelve el texto, o None si cancela
        o si las dos entradas no coinciden."""
        c1, ok = QInputDialog.getText(
            parent,
            "Crear contraseña de administrador",
            "Aún no hay contraseña de administrador.\nCrea una (mínimo 8 caracteres):",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return None
        c2, ok = QInputDialog.getText(
            parent,
            "Crear contraseña de administrador",
            "Repite la contraseña:",
            QLineEdit.EchoMode.Password
        )
        if not ok:
            return None
        if c1 != c2:
            GestorDiagnostico.mostrar_advertencia(parent, "Contraseña", "Las contraseñas no coinciden.")
            return None
        return c1
