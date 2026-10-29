from PyQt6.QtWidgets import QMenu
from PyQt6.QtGui import QAction

class GestorMenuContextual:
	@staticmethod
	def crear_menu_libreria(parent, item_seleccionado, callback_ver_separacion):
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
		accion_separacion.triggered.connect(lambda: callback_ver_separacion(item_seleccionado))
		menu.addAction(accion_separacion)

		return menu
		
