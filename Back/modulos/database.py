import sqlite3
import os
import stat

from modulos import config
from modulos.seguridad import sanitizar_nombre, validar_genero, ErrorSeguridad


class GestorBaseDatos:
    _COLUMNAS_PERMITIDAS = {"sintaxis_voz", "sintaxis_bajo", "sintaxis_otros"}

    def __init__(self, ruta_db=None):
        self.ruta_db = ruta_db or config.RUTA_DB
        self.inicializar_db()
        self._proteger_archivo()

    def _proteger_archivo(self):
        """Solo el propietario puede leer/escribir la BD (0600 en POSIX)."""
        try:
            if os.path.exists(self.ruta_db):
                os.chmod(self.ruta_db, stat.S_IRUSR | stat.S_IWUSR)
        except OSError:
            pass 
    def ejecutar_consulta(self, query, parametros=()):
        with sqlite3.connect(self.ruta_db) as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, parametros)
            conexion.commit()
            return cursor

    def inicializar_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS pistas_entrenamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT NOT NULL,
            bpm REAL NOT NULL,
            total_golpes INTEGER NOT NULL,
            sintaxis_bateria TEXT NOT NULL,
            sintaxis_voz TEXT NOT NULL,
            sintaxis_bajo TEXT NOT NULL,
            sintaxis_otros TEXT NOT NULL,
            genero TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.ejecutar_consulta(query)
        self.actualizar_esquema()

    def actualizar_esquema(self):
        columnas_nuevas = [
            ("sintaxis_voz", "TEXT DEFAULT ''"),
            ("sintaxis_bajo", "TEXT DEFAULT ''"),
            ("sintaxis_otros", "TEXT DEFAULT ''")
        ]
        with sqlite3.connect(self.ruta_db) as conexion:
            cursor = conexion.cursor()
            cursor.execute("PRAGMA table_info(pistas_entrenamiento)")
            columnas_existentes = [col[1] for col in cursor.fetchall()]
            
            for col_nombre, col_tipo in columnas_nuevas:
                if col_nombre not in self._COLUMNAS_PERMITIDAS:
                    raise ErrorSeguridad(f"Columna no permitida: {col_nombre}")
                if col_nombre not in columnas_existentes:
                    cursor.execute(f"ALTER TABLE pistas_entrenamiento ADD COLUMN {col_nombre} {col_tipo}")  # nosec: columna validada contra lista blanca
            conexion.commit()

    def guardar_registro(self, nombre_pista, bpm, golpes, cadena_bateria, cadena_voz, cadena_bajo, cadena_otros, genero):
        nombre_pista = sanitizar_nombre(nombre_pista)
        if not (0 <= float(bpm) <= 400) or int(golpes) < 0:
            raise ErrorSeguridad("Valores de BPM o golpes fuera de rango.")
        if genero != "Entrenamiento":
            genero = validar_genero(genero)
        query = """
        INSERT INTO pistas_entrenamiento (
            nombre_archivo, bpm, total_golpes, 
            sintaxis_bateria, sintaxis_voz, sintaxis_bajo, sintaxis_otros, genero
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """
        self.ejecutar_consulta(
            query, 
            (nombre_pista, bpm, golpes, cadena_bateria, cadena_voz, cadena_bajo, cadena_otros, genero)
        )
        print("[+] [Base de Datos] Registro guardado correctamente.")  # sin datos del usuario en logs

    def borrar_ultimo_registro(self):
        query_check = "SELECT id, nombre_archivo FROM pistas_entrenamiento ORDER BY id DESC LIMIT 1"
        with sqlite3.connect(self.ruta_db) as conexion:
            cursor = conexion.cursor()
            cursor.execute(query_check)
            resultado = cursor.fetchone()
            
            if resultado:
                id_borrar, nombre = resultado
                cursor.execute("DELETE FROM pistas_entrenamiento WHERE id = ?", (id_borrar,))
                conexion.commit()
                print("[+] [Base de Datos] Registro eliminado correctamente.")
            else:
                print("[-] [Base de Datos] La tabla está vacía, no hay nada que borrar.")

    def limpiar_base(self):

        query = "DELETE FROM pistas_entrenamiento"
        self.ejecutar_consulta(query)
        print("Se eliminaron los registros de prueba")

    def eliminar_anomalias(self):

        query = """
        DELETE FROM pistas_entrenamiento
        WHERE bpm <= 0
            OR total_golpes < 0
            OR sintaxis_bateria = ''
            OR sintaxis_bateria IS NULL
        """
        self.ejecutar_consulta(query)
        print("Se eliminaron registros anomalos")

    def entrenamiento(self):
        query = """
        SELECT sintaxis_bateria, sintaxis_voz, sintaxis_bajo, sintaxis_otros, genero 
        FROM pistas_entrenamiento
        """
        with sqlite3.connect(self.ruta_db) as conexion:
            cursor = conexion.cursor()
            cursor.execute(query)
            return cursor.fetchall()
