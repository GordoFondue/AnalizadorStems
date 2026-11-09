from PyQt6.QtWidgets import QLineEdit, QCompleter, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QStringListModel

class BuscadorPistas(QLineEdit):
    pista_elegida =pyqtSignal(str)

    def __init__(self,placeholder="Buscar pista..."):
        super().__init__()
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)
        self.setMinimumWidth(220)
        self.setMaximumWidth(360)

        self.setStyleSheet("""
            QLineEdit{
                background-color:#2b2b2b;
                color:#ffffff;
                border:1px solid #3d3d3d;
                border-radius: 6px;
                padding:6px 10px;
                font-size:12px;
                }
            QLineEdit:focus{
                border:1px solid #1db954;
            }
        """)
        self._modelo= QStringListModel(self)
        self._completer = QCompleter(self._modelo, self)
        self._completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self._completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self._completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self._completer.setMaxVisibleItems(8)
        self._completer.popup().setStyleSheet("""
            QListView {
             background-color:#181818;
             color:#e0e0e0;
             border:1px solid #3d3d3d;
             padding: 4px;
             font-size: 12px;
            }
            QListView::item:selected {
                background-color:#1db954;
                color:#ffffff;
            }
        """)
        self.setCompleter(self._completer)
        self._completer.activated[str].connect(self._al_activar)

    def establecer_pistas(self,nombre):
        self._modelo.setStringList(list(nombre))
        
    def establecer_actual(self,nombre):
        self.setText(nombre or "")
        
    def _al_activar(self, texto):
        self.pista_elegida.emit(texto)
        
    def _mostrar_todas(self):
        self.selectAll()
        self._completer.setCompletionPrefix("")
        self._completer.complete()
        
    def mousePressEvent(self,evento):
        super().mousePressEvent(evento)
        self._mostrar_todas()
            
    def keyPressEvent(self,evento):
        super().keyPressEvent(evento)
        if evento.key() == Qt.Key.Key_Down and not self._completer.popup().isVisible():
            self._mostrar_todas()
            
class BannerEstados(QLabel):
    _ESTILOS = {
        "OK":("#1db954","#10261a","#1db954"),
        "INFO":("#a0a0a0","#181818","#2a2a2a"),
        "AVISO":("#f0a500","#2a2210","#f0a500"),
        "ERROR":("#ff5252","#2a1212","#ff5252")
        }

    def __init__(self):
        super().__init__()
        self.setWordWrap(True)
        self.setVisible(False)
        
    def mostrar(self,texto, tipo="INFO"):
        color, fondo, borde = self._ESTILOS.get(tipo, self._ESTILOS["INFO"])
        self.setStyleSheet(
            f"color:{color}; background-color:{fondo}; border:1px solid {borde};"
            "border-radius:6px; padding:6px 10px; font-size:12px; font-weight: bold;"
        )
        self.setText(texto)
        self.setVisible(True)

    def ocultar(self):
        self.setText("")
        self.setVisible(False)
    
