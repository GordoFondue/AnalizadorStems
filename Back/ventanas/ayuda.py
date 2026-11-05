from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
from PyQt6.QtCore import Qt

class DialogoAyuda(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setWindowTitle("Ayuda- Analizador de Stems y patrones Musicales")
        self.resize(650,500)
        self._inicializar_ui()
        
    def _inicializar_ui(self):
        self.setStyleSheet("""
            QDialog{
                background-color:#121212;
                color:#e0e0e0;
            }
            QLabel{
                color:#e0e0e0;
                font-size:13px;
            }
            QScrollArea{
                border:none ;
                background-color: transparent;
            }
        """)

        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(20,20,20,20)
        layout_principal.setSpacing(15)

        titulo = QLabel("Guia de usuario y ayuda del sistema")
        titulo .setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1db954;
        """)
        layout_principal.addWidget(titulo)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        container  = QWidget()
        layout_contenido = QVBoxLayout(container)
        layout_contenido.setContentsMargins(10,10,10,10)
        layout_contenido.setSpacing(15)

        texto_ayuda= """
            <b style='color: #1db954; font-size: 14px;'>Paso 1: Carga y Procesamiento de Canciones</b><br>
        • Dirígete a la pestaña <b>Librería</b>.<br>
        • Haz clic en el botón <b>"Seleccionar archivos"</b> y elige una pista de audio (formatos <i>.mp3, .wav, .flac</i>).<br>
        • El sistema procesará automáticamente el audio utilizando Demucs para separar las fuentes, extraerá el BPM, calculará los transitorios de percusión y generará las cadenas simbólicas mediante modelos de mezcla gaussiana (GMM).<br><br>

        <b style='color: #1db954; font-size: 14px;'>Paso 2: Exploración y Reproducción de Stems</b><br>
        • Haz clic derecho sobre cualquier canción en la tabla de la librería y selecciona <b>"Ver Separación de Fuentes"</b>.<br>
        • En esta pestaña encontrarás tarjetas independientes para cada fuente (Voz, Batería, Bajo, Otros).<br>
        • Puedes reproducir/pausar cada stem de forma aislada y utilizar la <b>barra de progreso interactiva (slider)</b> con el mouse para saltar al minuto exacto de la pista.<br><br>

        <b style='color: #1db954; font-size: 14px;'>Paso 3: Análisis Estructural y Clasificación HMM</b><br>
        • Haz clic derecho en la librería y selecciona <b>"Ver Clasificación y Análisis HMM"</b>.<br>
        • Se mostrará un panel estilo dashboard con tarjetas modulares que detallan el género predicho por el modelo Oculto de Markov (HMM), los BPM y las métricas estructurales.<br><br>

        <b style='color: #1db954; font-size: 14px;'>Paso 4: Interpretación de Gráficas y el Abecedario Simbólico</b><br>
        • <b>Gráfica de Dispersión GMM:</b> Muestra en un plano cartesiano (Velocidad vs. Densidad Rítmica) los clústeres de los segmentos de audio agrupados por estados gaussianos. Las 'X' marcan los centroides de cada clúster.<br>
        • <b>Abecedario de Letras (Símbolos):</b><br>
          &nbsp;&nbsp;&nbsp;&nbsp;- <b>Batería (A, B, C, D, E):</b> Representa los estados de densidad rítmica y velocidad de transitorios.<br>
          &nbsp;&nbsp;&nbsp;&nbsp;- <b>Voz (X, Y, Z):</b> Evalúa la energía vocal y la tasa de cruces por cero (textura).<br>
          &nbsp;&nbsp;&nbsp;&nbsp;- <b>Bajo (B1, B2, B3):</b> Mide la frecuencia fundamental ($f_0$) y energía en bajas frecuencias.<br>
          &nbsp;&nbsp;&nbsp;&nbsp;- <b>Otros (O1, O2, O3):</b> Analiza el brillo espectral y coeficientes armónicos (MFCC).
                
        """

        lbl_detalles = QLabel(texto_ayuda)
        lbl_detalles.setWordWrap(True)
        layout_contenido.addWidget(lbl_detalles)

        scroll_area.setWidget(container)
        layout_principal.addWidget(scroll_area)

        btn_cerrar = QPushButton("Entendido")
        btn_cerrar.setStyleSheet("""
            QPushButton{
                background-color: #1db954;
                color:#ffffff;
                border-radius: 6px;
                padding: 8px 16px ;
                font-weight: bold ;
            } 
            QPushButton:hover {
                background-color:#1ed760;
            }
        """)

        btn_cerrar.clicked.connect(self.accept)
        layout_principal.addWidget(btn_cerrar, alignment=Qt.AlignmentFlag.AlignRight)

        self.setLayout(layout_principal)

        
