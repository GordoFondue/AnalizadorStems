import os
import sys
import multiprocessing

from modulos import config


def _preparar_salida():
    """En el ejecutable no hay consola: se manda todo a un archivo de registro
    (así puedes ver los errores) y se evitan fallos por stdout/stderr = None."""
    if not config.EMPAQUETADO:
        return
    os.makedirs(config.CARPETA_DATOS, exist_ok=True)
    ruta_log = os.path.join(config.CARPETA_DATOS, "AnalizadorStems.log")
    modo = "w" if os.path.exists(ruta_log) and os.path.getsize(ruta_log) > 2_000_000 else "a"
    log = open(ruta_log, modo, buffering=1, encoding="utf-8")
    sys.stdout = log
    sys.stderr = log


def main():
    multiprocessing.freeze_support()   # necesario en ejecutables con torch/joblib
    _preparar_salida()

    import matplotlib
    try:
        matplotlib.use("QtAgg")
    except Exception:
        pass

    from PyQt6.QtWidgets import QApplication
    from interface.window_main import WindowMain

    app = QApplication(sys.argv)
    ventana = WindowMain()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
