
import os
import sys
import getpass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modulos.seguridad import generar_hash_contrasena, ErrorSeguridad


def main():
    c1 = getpass.getpass("Nueva contraseña de administrador: ")
    c2 = getpass.getpass("Repite la contraseña: ")
    if c1 != c2:
        print("Las contraseñas no coinciden.")
        return
    try:
        hash_admin = generar_hash_contrasena(c1)
    except ErrorSeguridad as e:
        print(e)
        return
    print("\nAgrega esta línea a tu archivo .env:\n")
    print(f"APP_ADMIN_HASH={hash_admin}")


if __name__ == "__main__":
    main()
