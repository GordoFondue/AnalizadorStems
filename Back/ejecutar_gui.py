import sys
from PyQt6.QtWidgets import QApplication
from interface.window_main import WindowMain

def main():
    app = QApplication(sys.argv)
    
    ventana = WindowMain()
    
    ventana.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
