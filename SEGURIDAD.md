# Seguridad y manejo de datos sensibles

## 1. Secretos y credenciales
- Auditoría: **no se encontraron contraseñas, API keys ni tokens hardcodeados** en el código.
- Toda configuración se lee desde variables de entorno o `.env` (`modulos/config.py`).
- `.env` está en `.gitignore`; la plantilla pública es `.env.example` (sin valores reales).
- Si se agrega una API/clave en el futuro: `config.obtener("NOMBRE", requerida=True)`. Nunca en el código.
- Verificación automática: `python scripts/auditar_seguridad.py` (código de salida 1 si hay hallazgos; úsalo en pre-commit/CI).

## 2. Vulnerabilidades corregidas
| Riesgo | Corrección |
|---|---|
| Ruta personal `C:\Users\bryan\...` en tests (dato personal expuesto) | Ruta relativa al proyecto |
| Path traversal (nombre de pista usado para armar rutas) | `ruta_dentro_de()` + `sanitizar_nombre()` en `separador.py` y `separacion.py` |
| Inyección de opciones al comando `demucs` (nombres que empiezan con `-`) | Nombre saneado; `subprocess` con lista, sin `shell=True` |
| Archivos arbitrarios / muy grandes | `validar_audio()`: solo `.mp3`, límite configurable (100 MB) |
| SQL dinámico en `ALTER TABLE` | Lista blanca de columnas |
| Entradas sin validar (género, BPM, golpes) | `validar_genero()` y rangos en `guardar_registro()` |
| BD legible por otros usuarios | `chmod 600` al archivo de la BD (POSIX) |
| Logs con nombres de canciones y rutas locales | Logs sin datos del usuario; `ocultar_ruta()` en errores |
| Copia temporal normalizada queda en disco | Se elimina al terminar el procesamiento |
| `patrones_musicales.db` incluida en el zip pese a `.gitignore` | Excluida de la entrega |

Consultas SQL de `librery.py`/`clasificacion.py` (no modificadas): ya usan parámetros `?`, sin riesgo de inyección.

## 3. Cumplimiento legal (RGPD / LFPDPPP en México)
La app es local y casi no trata datos personales (nombres de archivo; los nombres de artista/título normalmente no son datos personales). Aun así:
- **Minimización**: solo se guarda lo necesario; temporales se borran.
- **Supresión**: ya existe "Eliminar registro" (derecho de cancelación/supresión).
- **Sin transmisión a terceros**: todo se procesa localmente (Demucs local).
- **Si algún día se agrega nube, cuentas o telemetría**: aviso de privacidad, base legal/consentimiento, cifrado en tránsito (TLS) y en reposo (SQLCipher con `APP_DB_KEY`).

## 4. Pendiente recomendado (requiere red / decisiones tuyas)
- `pip-audit` y `bandit -r .` en tu equipo para revisar dependencias y código.
- Fijar versiones en `requirements.txt` (`pip freeze`) y revisarlas periódicamente.
- `librery.py`: el filtro `LIKE` no escapa `%` y `_` (solo afecta resultados, no es inyección) y `clasificacion.py`/`librery.py` imprimen excepciones completas en consola. No los toqué, por tu indicación.
- Antes de compilar con PyInstaller, no incluir `.env` ni la `.db` en `datas`.
