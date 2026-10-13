import sqlite3
import os

class GestorBaseDatos:
    def __init__(self, ruta_db="patrones_musicales.db"):
        self.ruta_db = ruta_db
        self._inicializar_db()

    def _ejecutar_consulta(self, query, parametros=()):
        with sqlite3.connect(self.ruta_db) as conexion:
            cursor = conexion.cursor()
            cursor.execute(query, parametros)
            conexion.commit()
            return cursor

    def _inicializar_db(self):
        query = """
        CREATE TABLE IF NOT EXISTS pistas_entrenamiento (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_archivo TEXT NOT NULL,
            bpm REAL NOT NULL,
            total_golpes INTEGER NOT NULL,
            sintaxis_bateria TEXT NOT NULL,
            genero TEXT NOT NULL,
            fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self._ejecutar_consulta(query)

    def guardar_registro(self, nombre_pista, bpm, golpes, cadena_bateria, genero):
        query = """
        INSERT INTO pistas_entrenamiento (nombre_archivo, bpm, total_golpes, sintaxis_bateria, genero)
        VALUES (?, ?, ?, ?, ?)
        """
        self._ejecutar_consulta(query, (nombre_pista, bpm, golpes, cadena_bateria, genero))
        print(f"[+] [Base de Datos] Registro SQL exitoso para: {nombre_pista} ({genero})")

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