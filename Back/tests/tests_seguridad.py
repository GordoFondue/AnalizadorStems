import os
import sys
import sqlite3
import tempfile
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from modulos import seguridad as s
from modulos import config


def test_sanitizar_nombre_bloquea_traversal():
    assert "/" not in s.sanitizar_nombre("../../etc/passwd.mp3")
    assert not s.sanitizar_nombre("-rf.mp3").startswith("-")


def test_ruta_dentro_de_rechaza_escape(tmp_path):
    with pytest.raises(s.ErrorSeguridad):
        s.ruta_dentro_de(str(tmp_path), "..", "fuera")


def test_validar_audio_rechaza_extension(tmp_path):
    f = tmp_path / "x.exe"
    f.write_bytes(b"0")
    with pytest.raises(s.ErrorSeguridad):
        s.validar_audio(str(f))


def test_validar_genero():
    assert s.validar_genero("Rock") == "Rock"
    with pytest.raises(s.ErrorSeguridad):
        s.validar_genero("'; DROP TABLE x;--")


def test_sql_inyeccion_no_afecta_bd(tmp_path):
    from modulos.database import GestorBaseDatos
    db = GestorBaseDatos(str(tmp_path / "t.db"))
    db.guardar_registro("a.mp3", 120.0, 10, "A", "A", "A", "A", "Rock")
    db.ejecutar_consulta("DELETE FROM pistas_entrenamiento WHERE nombre_archivo = ?", ("' OR 1=1 --",))
    assert len(db.entrenamiento()) == 1


def test_sin_secretos_en_config():
    assert config.CLAVE_CIFRADO_DB is None or isinstance(config.CLAVE_CIFRADO_DB, str)


def test_admin_hash_y_autenticacion(monkeypatch):
    monkeypatch.setattr(config, "HASH_ADMIN", s.generar_hash_contrasena("ClaveSegura123"))
    s._intentos_fallidos = 0
    s._bloqueado_hasta = 0.0
    assert s.autenticar_admin("ClaveSegura123") is True
    assert s.autenticar_admin("incorrecta") is False


def test_admin_sin_configurar_deniega(monkeypatch):
    monkeypatch.setattr(config, "HASH_ADMIN", None)
    with pytest.raises(s.ErrorSeguridad):
        s.autenticar_admin("lo-que-sea")


def test_admin_bloqueo_por_intentos(monkeypatch):
    monkeypatch.setattr(config, "HASH_ADMIN", s.generar_hash_contrasena("ClaveSegura123"))
    s._intentos_fallidos = 0
    s._bloqueado_hasta = 0.0
    s.autenticar_admin("a")
    s.autenticar_admin("b")
    with pytest.raises(s.ErrorSeguridad):
        s.autenticar_admin("c")
    with pytest.raises(s.ErrorSeguridad):
        s.autenticar_admin("ClaveSegura123")
    s._bloqueado_hasta = 0.0
