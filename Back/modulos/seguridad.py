import os
import re
import hmac
import hashlib
import secrets
import time

from modulos import config

EXTENSIONES_PERMITIDAS = (".mp3",)
LONGITUD_MAX_NOMBRE = 150
LONGITUD_MAX_GENERO = 50
_CARACTERES_INVALIDOS = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
_PATRON_GENERO = re.compile(r"^[\w\s\-\.&'/áéíóúüñÁÉÍÓÚÜÑ]+$")


class ErrorSeguridad(ValueError):
    pass


def sanitizar_nombre(nombre: str) -> str:
    base = os.path.basename(str(nombre).replace("\\", "/"))
    base = _CARACTERES_INVALIDOS.sub("_", base).strip(" .")
    base = base.lstrip("-")
    if not base:
        raise ErrorSeguridad("Nombre de archivo vacío o inválido.")
    return base[:LONGITUD_MAX_NOMBRE]


def validar_genero(genero: str) -> str:
    genero = (genero or "").strip()
    if not genero or len(genero) > LONGITUD_MAX_GENERO or not _PATRON_GENERO.match(genero):
        raise ErrorSeguridad("Género inválido (máx. 50 caracteres, sin símbolos especiales).")
    return genero


def validar_audio(ruta: str, max_mb: int = 100) -> str:
    if not ruta or not os.path.isfile(ruta):
        raise FileNotFoundError(f"El archivo de audio no existe: {os.path.basename(str(ruta))}")
    if not ruta.lower().endswith(EXTENSIONES_PERMITIDAS):
        raise ErrorSeguridad("Formato no permitido. Solo se aceptan archivos .mp3.")
    if os.path.getsize(ruta) > max_mb * 1024 * 1024:
        raise ErrorSeguridad(f"El archivo supera el límite de {max_mb} MB.")
    return os.path.abspath(ruta)


def ruta_dentro_de(raiz: str, *partes: str) -> str:
    raiz_real = os.path.realpath(raiz)
    candidata = os.path.realpath(os.path.join(raiz_real, *partes))
    if os.path.commonpath([raiz_real, candidata]) != raiz_real:
        raise ErrorSeguridad("Ruta fuera del directorio permitido.")
    return candidata


def ocultar_ruta(texto: str) -> str:
    home = os.path.expanduser("~")
    return str(texto).replace(home, "~") if home else str(texto)


# ---------------------------------------------------------------------------
# Autenticación de administrador (protege la edición/ingreso de géneros)
# La contraseña NUNCA se guarda en texto plano: solo su hash PBKDF2 en .env
# ---------------------------------------------------------------------------
ITERACIONES_PBKDF2 = 310_000
LONGITUD_MIN_CONTRASENA = 8
MAX_INTENTOS_ADMIN = 3
BLOQUEO_SEGUNDOS = 60

_intentos_fallidos = 0
_bloqueado_hasta = 0.0


def generar_hash_contrasena(contrasena: str, iteraciones: int = ITERACIONES_PBKDF2) -> str:
    if not contrasena or len(contrasena) < LONGITUD_MIN_CONTRASENA:
        raise ErrorSeguridad(
            f"La contraseña debe tener al menos {LONGITUD_MIN_CONTRASENA} caracteres.")
    sal = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", contrasena.encode("utf-8"), sal, iteraciones)
    return f"pbkdf2_sha256${iteraciones}${sal.hex()}${digest.hex()}"


def _hash_valido(contrasena: str, almacenado: str) -> bool:
    try:
        algoritmo, iteraciones, sal_hex, hash_hex = almacenado.strip().split("$")
        if algoritmo != "pbkdf2_sha256":
            return False
        calculado = hashlib.pbkdf2_hmac(
            "sha256", contrasena.encode("utf-8"), bytes.fromhex(sal_hex), int(iteraciones))
        return hmac.compare_digest(calculado, bytes.fromhex(hash_hex))
    except (ValueError, TypeError, AttributeError):
        return False


def admin_configurado() -> bool:
    return bool((config.HASH_ADMIN or "").strip())


def autenticar_admin(contrasena: str) -> bool:
    """True si la contraseña es correcta, False si es incorrecta.
    Lanza ErrorSeguridad si no hay contraseña configurada o si hay bloqueo temporal."""
    global _intentos_fallidos, _bloqueado_hasta

    if not admin_configurado():
        raise ErrorSeguridad(
            "No hay contraseña de administrador configurada. "
            "Genera una con scripts/generar_hash_admin.py y colócala en el archivo .env.")

    restante = _bloqueado_hasta - time.monotonic()
    if restante > 0:
        raise ErrorSeguridad(
            f"Demasiados intentos fallidos. Espera {int(restante) + 1} segundos.")

    if _hash_valido(contrasena or "", config.HASH_ADMIN):
        _intentos_fallidos = 0
        return True

    _intentos_fallidos += 1
    if _intentos_fallidos >= MAX_INTENTOS_ADMIN:
        _intentos_fallidos = 0
        _bloqueado_hasta = time.monotonic() + BLOQUEO_SEGUNDOS
        raise ErrorSeguridad(
            f"Demasiados intentos fallidos. Acceso bloqueado {BLOQUEO_SEGUNDOS} segundos.")
    return False


def establecer_contrasena_admin(contrasena: str) -> None:
    """Crea o cambia la contraseña de administrador desde el programa.
    Guarda APP_ADMIN_HASH en el .env de la raíz del proyecto y la activa de inmediato.
    Lanza ErrorSeguridad si la contraseña no cumple el mínimo o si no se puede escribir el .env."""
    global _intentos_fallidos, _bloqueado_hasta
    hash_admin = generar_hash_contrasena(contrasena)
    ruta = os.path.join(config._RAIZ_PROYECTO, ".env")
    try:
        lineas = []
        if os.path.isfile(ruta):
            with open(ruta, "r", encoding="utf-8-sig") as f:
                lineas = f.read().splitlines()
        lineas = [l for l in lineas if not l.strip().startswith("APP_ADMIN_HASH=")]
        lineas.append(f"APP_ADMIN_HASH={hash_admin}")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas) + "\n")
        try:
            os.chmod(ruta, 0o600)
        except OSError:
            pass
    except OSError:
        raise ErrorSeguridad("No se pudo guardar la contraseña en el archivo .env (revisa permisos).")
    os.environ["APP_ADMIN_HASH"] = hash_admin
    config.HASH_ADMIN = hash_admin
    _intentos_fallidos = 0
    _bloqueado_hasta = 0.0
