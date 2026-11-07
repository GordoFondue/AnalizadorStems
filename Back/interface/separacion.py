import os
import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QLineEdit
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl

from interface.tarjeta import TarjetaStem
from modulos.database import GestorBaseDatos

class Separacion(QWidget):
    def __init__(self):
        super().__init__()
        self.pistas_guardadas = []
        self.db = GestorBaseDatos()
        self.pista_actual = None
        self._inicializar_ui()
        self.cargar_historial_db()

    def showEvent(self,event):
    	super().showEvent(event)
    	self.cargar_historial_db()
    	if self.pista_actual and self.pista_actual not in self.pistas_guardadas:
    	    self.limpiar_stems()

    def cargar_historial_db(self):
        try:
            with sqlite3.connect(self.db.ruta_db) as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT nombre_archivo FROM pistas_entrenamiento")
                self.pistas_guardadas = [reg[0] for reg in cursor.fetchall()]
            self.filtrar_historial(self.input_buscar_sep.text())

            if self.pista_actual:
                items = self.listas_pistas.findItems(self.pista_actual, Qt.MatchFlag.MatchExactly)
                if items:
                    self.listas_pistas.blockSignals(True)
                    self.listas_pistas.setCurrentItem(items[0])
                    self.listas_pistas.blockSignals(False)
        except Exception as e:
            print(f"Error al cargar historial de separacion: {e}")
    def limpiar_stems(self):
        self.pista_actual = None
        for tarjeta in self.tarjetas_stems.values():
            tarjeta.player.stop()
            tarjeta.player.setSource(QUrl())

    def _inicializar_ui(self):
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(20,20,20,20)
        layout_principal.setSpacing(20)

        panel_izquierdo = QVBoxLayout()
        titulo_izq = QLabel("Pistas")
        titulo_izq.setStyleSheet("""
            color: #ffffff;
            font-weight: bold;
            font-size: 14px;
        """)
        panel_izquierdo.addWidget(titulo_izq)

        self.input_buscar_sep = QLineEdit()
        self.input_buscar_sep.setPlaceholderText("Buscar pista separada...")
        self.input_buscar_sep.textChanged.connect(self.filtrar_historial)
        self.input_buscar_sep.setStyleSheet("""
            QLineEdit {
                background-color:#2b2b2b;
                color:#ffffff;
                border: 1px solid #3d3d3d;
                border-radius: 6px;
                padding: 6px 10px;
                font-size:12px;
            }
            QLineEdit::focus{
                border: 1px solid #1db954;
            }
        """)
        panel_izquierdo.addWidget(self.input_buscar_sep)
        
        self.listas_pistas = QListWidget()
        self.listas_pistas.setStyleSheet("""
            QListWidget {
                background-color:#121212;
                color: #e0e0e0 ;
                border: 1px solid #2a2a2a ;
                border-radius: 8px ;
                padding: 5px ;
            }
        """)

        self.listas_pistas.currentTextChanged.connect(self.cargar_stems_pista)

        panel_izquierdo.addWidget(self.listas_pistas)

        container_izq = QWidget()
        container_izq.setLayout(panel_izquierdo)
        container_izq.setFixedWidth(250)
        layout_principal.addWidget(container_izq)

        panel_derecho = QVBoxLayout()
        titulo_der = QLabel("Separación de Fuentes")
        titulo_der.setStyleSheet("""
            color: #ffffff ;
            font-weight: bold ;
            font-size: 18px ;
        """)
        panel_derecho.addWidget(titulo_der)

        self.tarjetas_stems = {}

        stems_config = {
            "Vocals (Voz)":"vocals.wav",
            "Drums (Bateria)":"drums.wav",
            "Bass (Bajo)":"bass.wav",
            "Other (Otros)":"other.wav"
        }

        for nombre in stems_config.keys():
            tarjeta = TarjetaStem(nombre)
            panel_derecho.addWidget(tarjeta)
            self.tarjetas_stems[nombre] = tarjeta

        panel_derecho.addStretch()

        container_der = QWidget()
        container_der.setLayout(panel_derecho)
        layout_principal.addWidget(container_der)

        self.setLayout(layout_principal)

    def cargar_pista_seleccionada(self,nombre_pista):
        self.cargar_historial_db()
        if nombre_pista not in self.pistas_guardadas:
            return

        items = self.listas_pistas.findItems(nombre_pista, Qt.MatchFlag.MatchExactly)
        if items:
            self.listas_pistas.setCurrentItem(items[0])

    def cargar_stems_pista(self,nombre_pista):
        if not nombre_pista:
            return
            
        self.pista_actual= nombre_pista

        nombre_limpio = os.path.splitext(nombre_pista)[0]

        base_path = os.path.join("pistas_separadas",nombre_limpio,"htdemucs",nombre_limpio)

        stems_archivo = {
            "Vocals (Voz)":"vocals.wav",
            "Drums (Bateria)":"drums.wav",
            "Bass (Bajo)":"bass.wav",
            "Other (Otros)":"other.wav"
        }

        print(f"Buscando stems dinámicos para: {nombre_limpio} en ruta: {base_path}")
        
        for nombre_stem, archivo_wav in stems_archivo.items():
            ruta_completa = os.path.join(base_path, archivo_wav)

            if nombre_stem in self.tarjetas_stems:
                tarjeta = self.tarjetas_stems[nombre_stem]

                if os.path.exists(ruta_completa):
                    tarjeta.cargar_archivo_stem(ruta_completa)
                    print(f" Stem cargado con éxito ({nombre_stem}): {ruta_completa}")

                else:
                    print(f"Archivo no encontrado en disco para {nombre_stem}: {ruta_completa}")
    def filtrar_historial (self, texto):
        texto = texto.lower()
        filtradas = [p for p in self.pistas_guardadas if texto in p.lower()]
        self.actualizar_lista_visual(filtradas)

    def actualizar_lista_visual(self, lista):
        self.listas_pistas.clear()
        for pista in lista:
            self.listas_pistas.addItem(pista)
