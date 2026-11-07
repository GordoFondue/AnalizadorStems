import os 
import sqlite3
from PyQt6.QtWidgets import (
    QWidget,QVBoxLayout,QHBoxLayout,QLabel,QListWidget,QLineEdit,QScrollArea,QFrame,QGridLayout
)

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QToolTip
from PyQt6.QtGui import QCursor

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas 
from matplotlib.figure import Figure

from modulos.database import GestorBaseDatos
from modulos.simbolico import PreprocesadorSimbolico
from modulos.analizador import AnalizadorPercusion
from modulos.voz import AnalizadorVoz
from modulos.bajo import AnalizadorBajo
from modulos.otros import AnalizadorOtros

class TarjetaGrafica(QFrame):
    def __init__(self,titulo_tarjeta, figura,alto_minimo=260):
        super().__init__()
        self.titulo_tarjeta = titulo_tarjeta
        self.figura = figura
        self.alto_minimo=alto_minimo
        self._inicializar_ui()

    def _inicializar_ui(self):
        self.setStyleSheet("""
            TarjetaGrafica {
                background-color: #181818;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                margin: 6px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins (12,12,12,12)
        layout.setSpacing(8)

        self.lbl_titulo= QLabel(self.titulo_tarjeta)
        self.lbl_titulo.setStyleSheet("""
            color:#ffffff;
            font-weight: bold;
            font-size: 14px;
            border: none;
        """)

        layout.addWidget(self.lbl_titulo)

        if self.figura:
            self.canvas= CanvasInteractivo(self.figura,self.alto_minimo)
            self.canvas.setStyleSheet("background-color: transparent;")
            layout.addWidget(self.canvas)

        self.setLayout(layout)

class CanvasInteractivo(FigureCanvas):
    def __init__(self,figura,alto_minimo=260):
        super().__init__(figura)
        self.figura = figura
        self.setMinimumHeight(alto_minimo)
        self.setMouseTracking(True)
        self.mpl_connect("motion_notify_event",self._al_mover_mouse)
        self.mpl_connect("figure_leave_event",lambda e: QToolTip.hideText())

    def wheelEvent(self,event):
        event.ignore()

    def _al_mover_mouse(self, evento):
        if evento.inaxes is None:
            QToolTip.hideText()
            return

        texto = self._texto_bajo_cursor(evento)
        if texto:
            QToolTip.showText(QCursor.pos(),texto,self)
        else:
            QToolTip.hideText()
    def _texto_bajo_cursor(self,evento):
        ax = evento.inaxes

        for barra in ax.patches:
            if barra.contains(evento)[0]:
                indice = ax.patches.index(barra)
                etiquetas = [t.get_text() for t in ax.get_xticklabels()]
                nombre = etiquetas[indice] if indice < len(etiquetas) else "Stem"
                return f"{nombre}\n Ventanas: {int(barra.get_height())}"

        mapa_color = {}

        for col in ax.collections:
            etiqueta = col.get_label()
            if etiqueta and not etiqueta.startswith("_"):
                mapa_color[tuple(col.get_facecolor()[0])] = etiqueta.replace("Segmentos tipo ", "")

        etq_x = ax.get_xlabel() or "X"
        etq_y = ax.get_ylabel() or "Y"

        for col in ax.collections:
            if not hasattr(col, "get_offsets"):
                continue
            col.set_pickradius(6)
            dentro, info = col.contains(evento)
            if not dentro:
                continue
            x, y = col.get_offsets()[info["ind"][0]]
            simbolo = mapa_color.get(tuple(col.get_facecolor()[0]),"?")

            es_centroide = (col.get_label() or "").startswith("_") and len(col.get_offsets()) == 1
            titulo = f"Centroide {simbolo}" if es_centroide else f"Segmento tipo {simbolo}"
            return f"{titulo}\n {etq_x}: {x:.2f}\n{etq_y}:{y:.2f}"
        return None

class RecuadroSeccion(QFrame):
    def __init__(self,titulo, widget_izquierdo, widgets_derecha):
        super().__init__()
        self.setStyleSheet("""
            RecuadroSeccion {
                background-color: #121212;
                border:1px solid #2a2a2a;
                border-radius: 14px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12,12,12,12)
        layout.setSpacing(8)

        lbl = QLabel(titulo)
        lbl.setStyleSheet("color:#ffffff; font-weight:bold; font-size: 15px; border:none;")
        layout.addWidget(lbl)

        fila = QHBoxLayout()
        fila.setSpacing(10)
        fila.addWidget(widget_izquierdo, 3)
        columna = QVBoxLayout()
        for w in widgets_derecha:
            columna.addWidget(w)
        fila.addLayout(columna,2)
        layout.addLayout(fila)
       
class ClasificacionHMM(QWidget):
    def __init__(self):
        super().__init__()
        self.pistas_guardadas =[]
        self.pista_actual = None
        self.db = GestorBaseDatos()
        self._inicializar_ui()
        self.cargar_historial_db()

    def showEvent(self,event):
        super().showEvent(event)
        self.cargar_historial_db()
        if self.pista_actual and self.pista_actual not in self.pistas_guardadas:
            self.limpiar_analisis()

    def _inicializar_ui(self):
        layout_principal = QHBoxLayout()
        layout_principal.setContentsMargins(20,20,20,20)
        layout_principal.setSpacing(20)

        panel_izquierdo = QVBoxLayout()
        titulo_izq = QLabel("Historial de Clasificación")
        titulo_izq.setStyleSheet("""
            color: #ffffff;
            font-weight: bold ;
            font-size: 14px ;
        """)

        panel_izquierdo.addWidget(titulo_izq)
        self.input_buscar_clas = QLineEdit()
        self.input_buscar_clas.setPlaceholderText ("Buscar pista analizada...")
        self.input_buscar_clas.textChanged.connect(self.filtrar_historial)
        self.input_buscar_clas.setStyleSheet("""
            QLineEdit {
                background-color: #2b2b2b;
                color:#ffffff;
                border:1px solid #3d3d3d;
                border-radius: 6px;
                padding:6px 10px;
                font-size:12px;
                
            } 
            QLineEdit::focus{
                border: 1px solid #1db954;
            }

        """)
        panel_izquierdo.addWidget(self.input_buscar_clas)


        self.listas_pistas = QListWidget()
        self.listas_pistas.setStyleSheet("""
            QListWidget{
                background-color: #121212;
                color: #e0e0e0;
                border: 1px solid #2a2a2a;
                border-radius: 8px;
                padding: 5px;
            }
        """)
        self.listas_pistas.currentTextChanged.connect(self.cargar_analisis_pista)
        panel_izquierdo.addWidget(self.listas_pistas)

        container_izq = QWidget()
        container_izq.setLayout(panel_izquierdo)
        container_izq.setFixedWidth(250)
        layout_principal.addWidget(container_izq)

        panel_derecho = QVBoxLayout()
        titulo_der = QLabel("Clasificación de Estructura y HMM")
        titulo_der.setStyleSheet("""
            color: #ffffff;
            font-weight: bold;
            font-size: 18px;
        """)
        panel_derecho.addWidget(titulo_der)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: transparent;
                border: none;
            }
        """)

        self.contenedor_tarjetas = QWidget()
        self.grid_tarjetas= QGridLayout(self.contenedor_tarjetas)
        self.grid_tarjetas.setContentsMargins(0,0,0,0)
        self.grid_tarjetas.setSpacing(15)

        self.scroll_area.setWidget(self.contenedor_tarjetas)
        panel_derecho.addWidget(self.scroll_area)

        container_der= QWidget()
        container_der.setLayout(panel_derecho)
        layout_principal.addWidget(container_der)

        self.setLayout(layout_principal)

        self.mostrar_tarjeta_bienvenida()


    def mostrar_tarjeta_bienvenida(self):
        fig = Figure(figsize=(5,3))
        ax = fig.add_subplot(111)
        ax.set_facecolor('#181818')
        fig.patch.set_facecolor('#181818')
        ax.text(0.5,0.5,"eleccione una pista del historial\npara ver el análisis HMM y gráficas",
            color='#a0a0a0', horizontalalignment= 'center', verticalalignment='center',fontsize=12)
        ax.axis('off')

        tarjeta = TarjetaGrafica("Estado del Sistema",fig)
        self.grid_tarjetas.addWidget(tarjeta, 0, 0)

    def cargar_historial_db (self):
        try:
            with sqlite3.connect(self.db.ruta_db) as conexion:
                cursor = conexion.cursor()
                cursor.execute ("SELECT nombre_archivo FROM pistas_entrenamiento")
                registros = cursor.fetchall()

                self.pistas_guardadas = [reg[0] for reg in registros]
                self.filtrar_historial(self.input_buscar_clas.text())
                self._reseleccionar_pista_actual()

        except Exception as e:
            print(f"Error al cargar historial de cllasificacion: {e}")

    def _reseleccionar_pista_actual(self):
        if not self.pista_actual:
            return
        items = self.listas_pistas.findItems(self.pista_actual, Qt.MatchFlag.MatchExactly)
        if items:
            self.listas_pistas.blockSignals(True)
            self.listas_pistas.setCurrentItem(items[0])
            self.listas_pistas.blockSignals(False)

    def limpiar_analisis(self):
        self.pista_actual = None
        self._vaciar_tarjetas()
        self.mostrar_tarjeta_bienvenida()

    def _vaciar_tarjetas(self):
        for r in range(self.grid_tarjetas.rowCount()):
            self.grid_tarjetas.setRowStretch(r,0)
        while self.grid_tarjetas.count():
            item = self.grid_tarjetas.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            
    def cargar_pista_seleccionada(self, nombre_pista):
        self.cargar_historial_db()
        if nombre_pista not in self.pistas_guardadas:
            return
        items = self.listas_pistas.findItems(nombre_pista,Qt.MatchFlag.MatchExactly)
        if items:
            self.listas_pistas.setCurrentItem(items[0])
    
    def cargar_analisis_pista(self, nombre_pista):
        if not nombre_pista:
            return

        print(f"Cargar analisis HMM y metricas para: {nombre_pista}")

        try:
            with sqlite3.connect(self.db.ruta_db) as conexion:
                cursor = conexion.cursor()
                cursor.execute("""
                    SELECT bpm, total_golpes, sintaxis_bateria, sintaxis_voz, sintaxis_bajo, sintaxis_otros, genero 
                    FROM pistas_entrenamiento WHERE nombre_archivo = ?
                """, (nombre_pista,))

                resultado = cursor.fetchone()

                if resultado:
                    self.pista_actual = nombre_pista
                    bpm, golpes, bat, voz, bajo, otros, genero = resultado
                    self.renderizar_tarjetas_analisis(nombre_pista, bpm, golpes, bat, voz, bajo, otros, genero)

        except Exception as e:
            print(f"Error consultando detalles de la pista: {e}")

    def renderizar_tarjetas_analisis (self,pista, bpm, golpes, bat, voz, bajo, otros, genero):
        self._vaciar_tarjetas()

        fig_resumen = Figure(figsize=(5 ,1.8))
        ax1= fig_resumen.add_subplot(111)
        ax1.set_facecolor("#181818")
        fig_resumen.patch.set_facecolor('#181818')

        texto_resumen = (
            f"Pista: {pista}\n"
            f"Género Predicho (HMM): {genero}\n"
            f"BPM: {bpm:.1f} | Golpes Totales: {golpes}"
        )

        ax1.text(0.05,0.5, texto_resumen, color='#ffffff', fontsize=11, verticalalignment='center')
        ax1.axis('off')
        tarjeta_resumen = TarjetaGrafica("Resumen de Clasificación HMM", fig_resumen, alto_minimo=110)

        fig_sintaxis = Figure(figsize=(5, 1.8))
        ax2= fig_sintaxis.add_subplot(111)
        ax2.set_facecolor('#181818')
        fig_sintaxis.patch.set_facecolor('#181818')

        s_bat = bat[:40] +"..." if len(bat) > 40 else bat
        s_voz = voz[:40] + "..." if len(voz) > 40 else voz
        s_bajo = bajo[:40] +"..." if len(bajo) > 40 else bajo
        s_otros = otros[:40] + "..." if len(otros) > 40 else otros

        texto_sintaxis = (
            f"Bateria [A-E]: {s_bat}\n"
            f"Voz [X-Z]: {s_voz}\n"
            f"Bajo [B1-B3]: {s_bajo}\n"
            f"Otros [01-03]: {s_otros}\n"
        )

        ax2.text(0.02,0.5, texto_sintaxis, color='#1db954', fontsize=10, fontweight='bold', verticalalignment='center')
        ax2.axis('off')
        tarjeta_sintaxis = TarjetaGrafica("Cadenas Simbólicas por Stem", fig_sintaxis, alto_minimo=110)
        
        fig_grafica = Figure(figsize =(10,2.8))
        ax3 = fig_grafica.add_subplot(111)
        ax3.set_facecolor('#181818')
        fig_grafica.patch.set_facecolor('#181818')

        stems_nombre = ['Batería','Voz','Bajo','Otros']

        longitudes = [len(bat.split('-')),len(voz.split('-')),len(bajo.split('-')),len(otros.split('-'))]

        bars = ax3.bar(stems_nombre,longitudes, color='#1db954',alpha=0.8,width=0.5)
        ax3.bar_label(bars,padding=3, color='#ffffff',fontsize=9)
        ax3.set_title("Densidad de Ventanas por Stem", color= '#ffffff', fontsize=10)

        ax3.tick_params(colors='#a0a0a0')
        ax3.spines['bottom'].set_color('#3d3d3d')
        ax3.spines['left'].set_color('#3d3d3d')
        ax3.spines['top'].set_visible(False)
        ax3.spines['right'].set_visible(False)
        fig_grafica.tight_layout()

        tarjeta_barras = TarjetaGrafica ("Métricas Estructurales de Stems", fig_grafica, alto_minimo=300)

        self.grid_tarjetas.addWidget(
            RecuadroSeccion("Informacion General",tarjeta_barras,[tarjeta_resumen,tarjeta_sintaxis]),
            0, 0
        )

        nombre_limpio= os.path.splitext(pista)[0]
        configuracion_stems = [
            ("Bateria","drums.wav",AnalizadorPercusion,['A','B','C'] ,
                lambda sim, c: f" Simbolo {sim}:\n {c[0]:.1f} BPM | {c[1]:.2f} golpes /s\n\n"),
            ("Voz","vocals.wav",AnalizadorVoz, ['X','Y','Z'],
                lambda sim, c:f"Simbolo {sim}:\n Energia: {c[0]:.1f} | Textura(ZCR): {c[1]:.2f}\n\n"),
            ("Bajo","bass.wav",AnalizadorBajo, ['B1','B2','B3'],
                lambda sim, c: f"Simbolo {sim}:\n Freq (Hz): {c[0]:.1f} | Energia RMS: {c[1]:.3f}\n\n"),
            ("Otros","other.wav",AnalizadorOtros, ['O1','O2','O3'],
                lambda sim, c: f"Simbolo{sim}:\n MFCC1: {c[0]:.1f} | Brillo Espectral: {c[1]:.2f}\n\n")
        ]
        fila =1
        for nombre,wav,clase_analizador,alfabeto,formato in configuracion_stems:
            if self._agregar_seccion_stem(fila,nombre_limpio,nombre,wav,clase_analizador,alfabeto,formato):
                fila +=1

        self.grid_tarjetas.setRowStretch(fila, 1)

    def _agregar_seccion_stem(self, fila, nombre_limpio,nombre,wav, clase_analizador,alfabeto,formato):
        try:
            ruta = os.path.join("pistas_separadas",nombre_limpio,"htdemucs", nombre_limpio, wav)
            if not os.path.exists(ruta):
                return False

            analizador = clase_analizador(ruta)
            secuencia = analizador.secuencia_temporal(ventana_segundos=10)
            if not secuencia or len(secuencia) < 3:
                return False

            preprocesador = PreprocesadorSimbolico(numero_estados=3)
            if alfabeto:
                preprocesador.alfabeto = alfabeto
            preprocesador.transformar(secuencia)

            fig_dispersion = preprocesador.graficar(secuencia)
            if not fig_dispersion:
                return False
            fig_dispersion.set_size_inches(5,3)
            fig_dispersion.tight_layout()
            
            tarjeta_disp = TarjetaGrafica(f"Gráfica de Dispersión GMM ({nombre})", fig_dispersion, alto_minimo=300)

            fig_info = Figure(figsize=(5,3))
            ax_info = fig_info.add_subplot(111)
            ax_info.set_facecolor('#181818')
            fig_info.patch.set_facecolor('#181818')
            detalles = f"Centroides GMM ({nombre}): \n \n"

            for idx,centro in enumerate (preprocesador.modelo.means_):
                detalles += formato(preprocesador.alfabeto[idx], centro)

            ax_info.text(0.05,0.5,detalles,color='#e0e0e0',fontsize=9,verticalalignment='center')
            ax_info.axis('off')
            fig_info.tight_layout()
            tarjeta_info = TarjetaGrafica(f"Detalles de Estado GMM ({nombre})", fig_info, alto_minimo=300)

            self.grid_tarjetas.addWidget(
                RecuadroSeccion(f"Analisis GMM: {nombre}",tarjeta_disp,[tarjeta_info]),
                fila, 0
            )
            return True
            
        except Exception as e:
            print(f"No se pudo cargar GMM {nombre}: {e}")
            traceback.print_exc()
            return False

    def filtrar_historial(self, texto):
        texto = texto.lower()
        filtradas = [p for p in self.pistas_guardadas if texto in p.lower()]
        self.actualizar_lista_visual(filtradas)

    def actualizar_lista_visual(self,lista):
        self.listas_pistas.clear()
        for pista in lista:
            self.listas_pistas.addItem(pista)

                
