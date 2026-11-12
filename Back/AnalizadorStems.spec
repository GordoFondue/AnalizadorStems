# -*- mode: python ; coding: utf-8 -*-
# Compilar con:   pyinstaller AnalizadorStems.spec --noconfirm --clean
# Genera la carpeta  dist/AnalizadorStems/  (modo "onedir": abre rápido y no se
# extrae en /tmp cada vez, a diferencia de --onefile).
import os
from PyInstaller.utils.hooks import collect_all, copy_metadata

datas, binaries, hiddenimports = [], [], []

# Paquetes con datos/módulos que PyInstaller no detecta solo
for paquete in ("demucs", "julius", "librosa", "lazy_loader", "hmmlearn",
                "sklearn", "soundfile", "soxr", "numba", "diffq", "lameenc", "openunmix"):
    try:
        d, b, h = collect_all(paquete)
        datas += d; binaries += b; hiddenimports += h
    except Exception as e:
        print(f"[spec] aviso: no se pudo recopilar {paquete}: {e}")

# Metadatos que torch/demucs/librosa consultan al arrancar
for paquete in ("torch", "torchaudio", "tqdm", "numpy", "scipy", "packaging",
                "filelock", "requests", "joblib", "scikit-learn", "hmmlearn"):
    try:
        datas += copy_metadata(paquete)
    except Exception:
        pass

# Datos iniciales (se copian a la carpeta del usuario en la primera ejecución).
# NO se empaqueta el .env (guarda secretos).
for archivo in ("patrones_musicales.db", "modelo_gmm.pkl"):
    if os.path.isfile(archivo):
        datas.append((archivo, "."))
    else:
        print(f"[spec] aviso: no existe {archivo}; se crea vacío en el primer arranque")

a = Analysis(
    ["ejecutar_gui.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        "matplotlib.backends.backend_qtagg", "PyQt6.QtMultimedia",
        "sklearn.utils._typedefs", "sklearn.neighbors._partition_nodes",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter", "pytest"],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AnalizadorStems",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="AnalizadorStems",
)
