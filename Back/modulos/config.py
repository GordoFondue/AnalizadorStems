import os

_RAIZ_PROYECTO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rutas_env_candidatas():
    """Lugares donde se busca el archivo .env (en orden de prioridad)."""
    rutas = [
        os.path.join(_RAIZ_PROYECTO, ".env"),
        os.path.join(os.getcwd(), ".env"),
    ]
    vistas, unicas = set(), []
    for r in rutas:
        r = os.path.abspath(r)
        if r not in vistas:
            vistas.add(r)
            unicas.append(r)
    return unicas


RUTA_ENV_CARGADO = None


def _cargar_dotenv(ruta=None):
    global RUTA_ENV_CARGADO
    candidatas = [ruta] if ruta else rutas_env_candidatas()
    for r in candidatas:
        if not os.path.isfile(r):
            continue
        try:
            with open(r, "r", encoding="utf-8-sig") as f:
                for linea in f:
                    linea = linea.strip()
                    if not linea or linea.startswith("#") or "=" not in linea:
                        continue
                    clave, valor = linea.split("=", 1)
                    clave = clave.strip()
                    valor = valor.strip().strip('"').strip("'")
                    # no pisa variables reales del entorno, salvo que estén vacías
                    if clave and not os.environ.get(clave):
                        os.environ[clave] = valor
            if RUTA_ENV_CARGADO is None:
                RUTA_ENV_CARGADO = r
        except OSError:
            pass


_cargar_dotenv()


def obtener(nombre, defecto=None, requerida=False):
    """Lee una variable de entorno. Si es requerida y falta, falla con claridad."""
    valor = os.environ.get(nombre, defecto)
    if requerida and (valor is None or str(valor).strip() == ""):
        raise RuntimeError(
            f"Falta la variable de entorno obligatoria '{nombre}'. "
            "Defínela en tu entorno o en el archivo .env (ver .env.example)."
        )
    return valor


def _entero(nombre, defecto):
    try:
        return int(obtener(nombre, defecto))
    except (TypeError, ValueError):
        return int(defecto)


RUTA_DB = obtener("APP_DB_PATH", os.path.join(_RAIZ_PROYECTO, "patrones_musicales.db"))
CARPETA_STEMS = obtener("APP_STEMS_DIR", os.path.join(_RAIZ_PROYECTO, "pistas_separadas"))
CARPETA_TEMPORAL = obtener("APP_TEMP_DIR", os.path.join(_RAIZ_PROYECTO, "separated"))
TAMANO_MAX_AUDIO_MB = _entero("APP_MAX_AUDIO_MB", 100)
DEBUG = str(obtener("APP_DEBUG", "0")).lower() in ("1", "true", "si", "yes")


CLAVE_CIFRADO_DB = obtener("APP_DB_KEY")

API_KEY_EXTERNA = obtener("APP_EXTERNAL_API_KEY")

# Hash PBKDF2 de la contraseña de administrador (generado con scripts/generar_hash_admin.py)
HASH_ADMIN = obtener("APP_ADMIN_HASH")
