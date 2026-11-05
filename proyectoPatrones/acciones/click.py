from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

class GestorMenuContextual:
    @staticmethod
    def crear_menu_libreria(parent, nombre_pista, callback_ver_separacion, callback_ver_clasificacion, callback_editar_genero, callback_eliminar_registro):
        menu = QMenu (parent)
        menu.setStyleSheet("""
            QMenu{
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 5px;
            }
            QMenu::item{
                padding: 6px 20px;
                border-radius: 4px;
            }
            QMenu::item:selected{
                background-color: #1db954;
                color: #ffffff;
            }
        """)

        accion_separacion = QAction ("Ver Separación de Fuentes", parent)
        accion_separacion.triggered.connect(lambda: callback_ver_separacion(nombre_pista))
        menu.addAction(accion_separacion)

        accion_clasificacion = QAction("Ver Clasificación y Análisis HMM", parent)
        accion_clasificacion.triggered.connect(lambda: callback_ver_clasificacion(nombre_pista))
        menu.addAction(accion_clasificacion)

        accion_editar = QAction("Editar Género Manualmente",parent)
        accion_editar.triggered.connect(lambda:callback_editar_genero(nombre_pista))
        menu.addAction(accion_editar)

        accion_eliminar = QAction("Eliminar Registro", parent)
        accion_eliminar.triggered.connect(lambda:callback_eliminar_registro(nombre_pista))
        menu.addAction(accion_eliminar)

        return menu
        
