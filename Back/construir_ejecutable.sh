#!/usr/bin/env bash
# Ejecutar desde la carpeta Back/ (donde está ejecutar_gui.py) con el venv activado.
set -e

# Seguridad: solo corre si estás en la carpeta correcta
if [ ! -f "ejecutar_gui.py" ] || [ ! -f "AnalizadorStems.spec" ]; then
    echo "ERROR: ejecuta este script dentro de la carpeta Back/ (donde está ejecutar_gui.py)."
    exit 1
fi

# Copia de respaldo de tu base de datos y modelo (por si acaso)
mkdir -p respaldo
[ -f patrones_musicales.db ] && cp -n patrones_musicales.db "respaldo/patrones_musicales_$(date +%Y%m%d_%H%M%S).db"
[ -f modelo_gmm.pkl ] && cp -n modelo_gmm.pkl "respaldo/modelo_gmm_$(date +%Y%m%d_%H%M%S).pkl"
echo "Respaldo guardado en la carpeta respaldo/"

# Solo borra las carpetas temporales que PyInstaller genera (build/ y dist/)
echo "Limpiando build/ y dist/ de compilaciones anteriores..."
rm -rf build dist

pyinstaller AnalizadorStems.spec --noconfirm --clean

echo
echo "Listo:  dist/AnalizadorStems/AnalizadorStems"
echo "Registro de errores en:  ~/.local/share/AnalizadorStems/AnalizadorStems.log"
