import os
import sqlite3
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtCore import QUrl
from PyQt6.QtCore import QTimer
from PyQt6.QtMultimedia import QMediaPlayer

from interface.tarjeta import TarjetaStem
from modulos.database import GestorBaseDatos
from interface.barra_superior import BuscadorPistas, BannerEstados
from ventanas.dialogos import GestorDiagnostico


def resolver_carpeta_stems(nombre_pista, raiz="pistas_separadas"):
    limpio = os.path.splitext(nombre_pista)[0]
    partes = limpio.split(" - ")
    candidatos = [" - ".join(partes[i:]) for i in range(len(partes))]

    for c in candidatos:
        base = os.path.join(raiz, c, "htdemucs", c)
        if os.path.isdir(base):
            return base
    for c in candidatos:
        base = os.path.join(raiz, c, "htdemucs", "temp_normalizado")
        if os.path.isdir(base):
            return base
    return os.path.join(raiz, limpio, "htdemucs", limpio)


class Separacion(QWidget):
    def __init__(self):
        super().__init__()
        self.pistas_guardadas = []
        self.db = GestorBaseDatos()
        self.pista_actual = None
        self.estado_stems = {}
        self.motivos_fallo = {}
        self._carga_notificada = True
        self._id_carga = 0
        self._inicializar_ui()
        self.cargar_historial_db()

    def showEvent(self, event):
        super().showEvent(event)
        self.cargar_historial_db()
        if self.pista_actual and self.pista_actual not in self.pistas_guardadas:
            self.limpiar_stems()

    def cargar_historial_db(self):
        try:
            with sqlite3.connect(self.db.ruta_db) as conexion:
                cursor = conexion.cursor()
                cursor.execute("SELECT nombre_archivo FROM pistas_entrenamiento")
                self.pistas_guardadas = [reg[0] for reg in cursor.fetchall()]
            self.actualizar_lista_visual(self.pistas_guardadas)
        except Exception as e:
            print(f"Error al cargar historial de separacion: {e}")
            GestorDiagnostico.mostrar_error(
                self, "No se pudo leer la base de datos",
                f"No se pudo cargar la lista de pistas:\n{e}"
            )

    def limpiar_stems(self):
        self.pista_actual = None
        for tarjeta in self.tarjetas_stems.values():
            tarjeta.player.stop()
            tarjeta.player.setSource(QUrl())
        self.estado_stems = {}
        self.buscador.establecer_actual("")
        self.banner.mostrar("La pista que estaba cargada ya no existe en la base de datos.", "AVISO")

    def _inicializar_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20, 20, 20, 20)
        layout_principal.setSpacing(12)

        barra_superior = QHBoxLayout()
        titulo_der = QLabel("Separación de Fuentes")
        titulo_der.setStyleSheet("""
            color: #ffffff ;
            font-weight: bold ;
            font-size: 18px ;
        """)
        barra_superior.addWidget(titulo_der)
        barra_superior.addStretch()

        self.buscador = BuscadorPistas("Buscar pista separada...")
        self.buscador.pista_elegida.connect(self.cargar_stems_pista)
        barra_superior.addWidget(self.buscador)
        layout_principal.addLayout(barra_superior)

        self.banner = BannerEstados()
        layout_principal.addWidget(self.banner)

        self.tarjetas_stems = {}

        stems_config = {
            "Vocals (Voz)": "vocals.wav",
            "Drums (Bateria)": "drums.wav",
            "Bass (Bajo)": "bass.wav",
            "Other (Otros)": "other.wav"
        }

        for nombre in stems_config.keys():
            tarjeta = TarjetaStem(nombre)
            layout_principal.addWidget(tarjeta, 1)
            self.tarjetas_stems[nombre] = tarjeta

            tarjeta.player.mediaStatusChanged.connect(
                lambda estado, n=nombre: self._al_cambiar_estado_media(n, estado))
            tarjeta.player.errorOccurred.connect(
                lambda error, mensaje, n=nombre: self._al_error_media(n, mensaje))

        self.setLayout(layout_principal)

    def _al_cambiar_estado_media(self, nombre_stem, estado):
        if nombre_stem not in self.estado_stems or self.estado_stems[nombre_stem] is not None:
            return
        if estado in (QMediaPlayer.MediaStatus.LoadedMedia, QMediaPlayer.MediaStatus.BufferedMedia):
            self.estado_stems[nombre_stem] = True
        elif estado == QMediaPlayer.MediaStatus.InvalidMedia:
            self.estado_stems[nombre_stem] = False
            self.motivos_fallo[nombre_stem] = "el archivo de audio no es válido o está dañado"
        else:
            return
        self._evaluar_estado()

    def _al_error_media(self, nombre_stem, mensaje):
        if nombre_stem in self.estado_stems and self.estado_stems[nombre_stem] is None:
            self.estado_stems[nombre_stem] = False
            self.motivos_fallo[nombre_stem] = mensaje or "error del reproductor"
            self._evaluar_estado()

    def _evaluar_estado(self):
        if not self.estado_stems or self._carga_notificada:
            return
        if any(v is None for v in self.estado_stems.values()):
            return

        self._carga_notificada = True
        nombre = self.pista_actual or ""
        fallidos = [n for n, ok in self.estado_stems.items() if not ok]
        if not fallidos:
            self.banner.mostrar(
                f" Los {len(self.estado_stems)} stems de '{nombre}' se cargaron correctamente y están listos para reproducir.",
                "OK")
        else:
            detalle = "\n".join(f"• {n}: {self.motivos_fallo.get(n, 'no se pudo cargar')}" for n in fallidos)
            buenos = len(self.estado_stems) - len(fallidos)
            self.banner.mostrar(
                f" Se cargaron {buenos} de {len(self.estado_stems)} stems de '{nombre}'. Fallaron: "
                + ", ".join(fallidos), "ERROR")
            GestorDiagnostico.mostrar_error(
                self, "Fallo al cargar stems",
                f"No se pudieron cargar los siguientes stems de '{nombre}':\n\n{detalle}"
            )

    def cargar_pista_seleccionada(self, nombre_pista):
        self.cargar_historial_db()
        if nombre_pista not in self.pistas_guardadas:
            GestorDiagnostico.mostrar_advertencia(
                self, "Pista no encontrada",
                f"'{nombre_pista}' ya no está en la base de datos."
            )
            return
        self.cargar_stems_pista(nombre_pista)

    def cargar_stems_pista(self, nombre_pista):
        if not nombre_pista:
            return

        self.pista_actual = nombre_pista
        self.buscador.establecer_actual(nombre_pista)

        base_path = resolver_carpeta_stems(nombre_pista)

        stems_archivo = {
            "Vocals (Voz)": "vocals.wav",
            "Drums (Bateria)": "drums.wav",
            "Bass (Bajo)": "bass.wav",
            "Other (Otros)": "other.wav"
        }

        print(f"Buscando stems dinámicos para: {nombre_pista} en ruta: {base_path}")

        self.estado_stems = {n: None for n in stems_archivo}
        self.motivos_fallo = {}
        self._carga_notificada = False
        self._id_carga += 1
        id_actual = self._id_carga
        self.banner.mostrar(f" Cargando stems de '{nombre_pista}'...", "INFO")

        for nombre_stem, archivo_wav in stems_archivo.items():
            ruta_completa = os.path.join(base_path, archivo_wav)

            if nombre_stem in self.tarjetas_stems:
                tarjeta = self.tarjetas_stems[nombre_stem]

                if os.path.exists(ruta_completa):
                    tarjeta.player.setSource(QUrl())
                    tarjeta.cargar_archivo_stem(ruta_completa)
                    print(f" Stem cargado con éxito ({nombre_stem}): {ruta_completa}")

                else:
                    print(f"Archivo no encontrado en disco para {nombre_stem}: {ruta_completa}")
                    tarjeta.player.stop()
                    tarjeta.player.setSource(QUrl())
                    self.estado_stems[nombre_stem] = False
                    self.motivos_fallo[nombre_stem] = f"no se encontró el archivo {archivo_wav} en:\n    {base_path}"

        self._evaluar_estado()
        QTimer.singleShot(10000, lambda: self._vencer_plazo(id_actual))

    def _vencer_plazo(self, id_carga):
        if id_carga != self._id_carga or self._carga_notificada:
            return
        for n, ok in self.estado_stems.items():
            if ok is None:
                self.estado_stems[n] = False
                self.motivos_fallo[n] = "el reproductor no respondió a tiempo"
        self._evaluar_estado()

    def actualizar_lista_visual(self, lista):
        self.buscador.establecer_pistas(lista)
