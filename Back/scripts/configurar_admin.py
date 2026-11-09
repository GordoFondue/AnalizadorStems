"""Define (o cambia) la contraseña de administrador y la guarda en el archivo .env

Funciona desde cualquier carpeta donde lo coloques (raíz del proyecto o scripts/):
    python configurar_admin.py          (o)   python scripts/configurar_admin.py

Escribe APP_ADMIN_HASH en el .env que el programa realmente lee (el de la
carpeta raíz del proyecto, donde está la carpeta 'modulos') y comprueba
al final que la contraseña quedó funcionando.
"""
import os
import sys
import stat
import getpass

_AQUI = os.path.dirname(os.path.abspath(__file__))
for _ruta in (_AQUI, os.path.dirname(_AQUI), os.getcwd()):
    if os.path.isdir(os.path.join(_ruta, "modulos")) and _ruta not in sys.path:
        sys.path.insert(0, _ruta)

try:
    from modulos import config
    from modulos.seguridad import generar_hash_contrasena, ErrorSeguridad
except ImportError as e:
    print(f"No se encontró la carpeta 'modulos' del proyecto: {e}")
    print("Coloca este script en la raíz del proyecto (junto a ejecutar_gui.py) o en scripts/.")
    sys.exit(1)

CLAVE = "APP_ADMIN_HASH"
_CLAVE_ERRONEA = "123456789"  # valor mal escrito por una versión anterior del script
RUTA_ENV = os.path.join(config._RAIZ_PROYECTO, ".env")


def guardar_hash_en_env(hash_admin, ruta=RUTA_ENV):
    lineas = []
    if os.path.isfile(ruta):
        with open(ruta, "r", encoding="utf-8-sig") as f:
            lineas = f.read().splitlines()

    # Limpia la línea errónea que dejó la versión anterior del script
    lineas = [l for l in lineas if not l.strip().startswith(f"{_CLAVE_ERRONEA}=")]

    nueva = f"{CLAVE}={hash_admin}"
    reemplazada = False
    for i, linea in enumerate(lineas):
        if linea.strip().startswith(f"{CLAVE}="):
            lineas[i] = nueva
            reemplazada = True
            break
    if not reemplazada:
        lineas.append(nueva)

    with open(ruta, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas) + "\n")
    try:
        os.chmod(ruta, stat.S_IRUSR | stat.S_IWUSR)
    except OSError:
        pass


def main():
    print("=== Configurar contraseña de administrador ===")
    print(f"Raíz del proyecto detectada: {config._RAIZ_PROYECTO}")
    print(f"Archivo .env a escribir:     {RUTA_ENV}\n")
    try:
        c1 = getpass.getpass("Nueva contraseña (mínimo 8 caracteres): ")
        c2 = getpass.getpass("Repite la contraseña: ")
    except (EOFError, KeyboardInterrupt):
        print("\nCancelado.")
        return

    if c1 != c2:
        print("Las contraseñas no coinciden. No se hizo ningún cambio.")
        return
    try:
        hash_admin = generar_hash_contrasena(c1)
    except ErrorSeguridad as e:
        print(e)
        return

    guardar_hash_en_env(hash_admin)

    # Verificación: recarga el .env como lo hace el programa y prueba la clave
    os.environ.pop(CLAVE, None)
    config._cargar_dotenv(RUTA_ENV)
    config.HASH_ADMIN = os.environ.get(CLAVE)
    from modulos import seguridad
    seguridad._intentos_fallidos = 0
    seguridad._bloqueado_hasta = 0.0
    if seguridad.admin_configurado() and seguridad.autenticar_admin(c1):
        print("\nListo. Contraseña guardada y verificada correctamente.")
        print(f"Guardada en: {RUTA_ENV}")
        print("Cierra y vuelve a abrir el programa (desde esta misma carpeta de proyecto).")
    else:
        print("\nSe escribió el archivo, pero no se pudo verificar. Revisa permisos de:")
        print(RUTA_ENV)


if __name__ == "__main__":
    main()
