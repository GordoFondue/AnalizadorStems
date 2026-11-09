import os 
import sys
import getpass
from PyQt6.QtWidgets import QApplication, QFileDialog
from controlador import ControladorAnalisis
from modulos.seguridad import (
    sanitizar_nombre, validar_genero, ErrorSeguridad,
    autenticar_admin, admin_configurado
)


def pedir_contrasena_admin():
    """Pide la contraseña (sin mostrarla). Devuelve True solo si es correcta."""
    if not admin_configurado():
        print("No hay contraseña de administrador configurada.")
        print("Genera una con scripts/generar_hash_admin.py y colócala en el archivo .env.")
        return False

    for _ in range(3):
        try:
            try:
                contrasena = getpass.getpass("Contraseña de administrador: ")
            except (EOFError, KeyboardInterrupt):
                print("\nAcceso cancelado.")
                return False
            if autenticar_admin(contrasena):
                return True
            print("Contraseña incorrecta.")
        except ErrorSeguridad as e:
            print(e)
            return False
    return False


def poblar_base():

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    print("Poblador de la base de datos")

    if not pedir_contrasena_admin():
        print("Acceso denegado. Solo el administrador puede ingresar géneros.")
        return
    print("Acceso concedido.")

    controlador = ControladorAnalisis()

    while True:
        print("\n" + "-"*50)
        opcion = input("¿Deseas ingresar el archivo o escribir la ruta?").strip()

        if opcion.lower() == 's':
            print("Hasta luego")
            break

        ruta_mp3 = ""
        if opcion == '1':
            ruta_mp3, _ = QFileDialog.getOpenFileName(
                None,
                "Selecciona el archivo MP3",
                "",
                "Archivos de audio"
            )
        elif opcion == '2':
            ruta_mp3 = input("ingresa o arrastra la ruta del archivo").strip()
            ruta_mp3 = ruta_mp3.strip('"\'')
        else:
            print("Opcion no valida")
            continue
        if not ruta_mp3:
            print("Archivo no seleccionado")
            continue
        if not os.path.exists(ruta_mp3) or not ruta_mp3.lower().endswith('.mp3'):
            print("El archivo no existe")
            continue

        nombres_archivo = os.path.basename(ruta_mp3)
        print("Archivo seleccionado correctamente")

        grupo = input("Ingresa el grupo o nombre del artista: ").strip()
        genero = input("Ingresa el genero al que pertenece").strip()

        try:
            genero = validar_genero(genero)
            nombre_final = sanitizar_nombre(
                f"{grupo} - {nombres_archivo}" if grupo else nombres_archivo)
        except ErrorSeguridad as e:
            print(f"Entrada no válida: {e}")
            continue

        print(f"\n Separando stems para '{nombre_final}'...")

        try:
            resultado = controlador.procesar_audio(ruta_mp3)

            if resultado.get("guardado_en_db", True):
                controlador.db.ejecutar_consulta(
                    """
                    UPDATE pistas_entrenamiento
                    SET genero = ?, nombre_archivo = ?
                    WHERE id = (SELECT MAX(id) FROM pistas_entrenamiento)
                    """,
                    (genero, nombre_final)
                )
                print("Canción guardada correctamente")
                print(f"Canción: {nombre_final}")


            else:
                print("No se guardo la cancion")

        except Exception as e:
            print("Ocurrio un error al procesar el archivo (revisa los datos ingresados).")
if __name__ == "__main__":
    poblar_base()
