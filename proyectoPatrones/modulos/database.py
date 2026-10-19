import sqlite3
import os

class GestorBaseDatos:
    def __init__(self, ruta_db="patrones_musicales.db"):
        self.ruta_db = ruta_db
        self.inicializar_db()

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
                if col_nombre not in columnas_existentes:
                    cursor.execute(f"ALTER TABLE pistas_entrenamiento ADD COLUMN {col_nombre} {col_tipo}")
            conexion.commit()

    def guardar_registro(self, nombre_pista, bpm, golpes, cadena_bateria, cadena_voz, cadena_bajo, cadena_otros, genero):
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
        print(f"[+] [Base de Datos] Registro exitoso de los 4 stems para: {nombre_pista} ({genero})")

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
                print(f"[+] [Base de Datos] Se eliminó con éxito el registro de '{nombre}'.")
            else:
                print("[-] [Base de Datos] La tabla está vacía, no hay nada que borrar.")
    def entrenamiento(self):
        query = """
        SELECT sintaxis_bateria, sintaxis_voz, sintaxis_bajo, sintaxis_otros, genero 
        FROM pistas_entrenamiento
        """
        with sqlite3.connect(self.ruta_db) as conexion:
            cursor = conexion.cursor()
            cursor.execute(query)
            return cursor.fetchall()