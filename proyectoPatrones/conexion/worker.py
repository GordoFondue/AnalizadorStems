import os 
from PyQt6.QtCore import QThread, pyqtSignal
from controlador import ControladorAnalisis

# -*- coding: utf-8 -*-

class WorkerProcesamiento(QThread):
    terminado = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, ruta_archivo, db=None):
        super().__init__()
        self.ruta_archivo = ruta_archivo
        self.controlador = ControladorAnalisis()

    def run(self):
        try:
            resultado = self.controlador.procesar_audio(self.ruta_archivo)            
            self.terminado.emit(resultado["nombre_pista"])
        except Exception as e:
            print(f"[-] Error crítico en el worker independiente: {e}")
            self.error.emit(str(e))