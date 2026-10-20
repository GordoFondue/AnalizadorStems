import sys
from PyQt6.QtWidgets import QApplication
from interface.window_main import WindowMain

def main():
    # 1. Inicializa la aplicación de PyQt6 (Obligatorio)
    app = QApplication(sys.argv)
    
    # 2. Instancia tu clase de la interfaz (POO)
    ventana = WindowMain()
    
    # 3. Muestra la ventana en la pantalla
    ventana.show()
    
    # 4. Ejecuta el ciclo de eventos de la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
