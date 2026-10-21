import os
from modulos.separador import MotorSeparacion
from modulos.analizador import AnalizadorPercusion
from modulos.voz import AnalizadorVoz
from modulos.bajo import AnalizadorBajo
from modulos.otros import AnalizadorOtros
from modulos.simbolico import PreprocesadorSimbolico
from modulos.database import GestorBaseDatos
from modulos.modeloHMM import ClasificadorEstructuraHMM

class AplicacionCLI:
    def __init__(self):
        self.separador = MotorSeparacion()
        self.stems = None
        self.resultados_analisis = None
        self.genero_predicho_hmm = None
        self.nombre_pista = None

    def iniciar(self):
        print("="*60)
        print("   SISTEMA DE RECONOCIMIENTO DE PATRONES MUSICALES (POO)")
        print("="*60)
        
        cancion = input("Ingresa la ruta de tu pista .mp3: ")
        self.nombre_pista_actual = os.path.basename(cancion)
        
        try:
            self.stems = self.separador.procesar_pista(cancion)
        except FileNotFoundError as e:
            print(f"[-] Error: {e}")
            return

        if self.stems:
            self.menu_inicial()
    def menu_inicial(self):
        while True:
            print("\n" + "="*50)
            print("        FASE 1: PROCESAMIENTO Y ANÁLISIS")
            print("="*50)
            print("1. Analizar Canción Completa (Batería, Voz, Bajo y Otros)")
            print("2. Salir")
            print("="*50)
            
            opcion = input("[>] Elige una opción: ")
            
            if opcion == "1":
                self.analizar_cancion()
                self.menu_consultas()
                break
            elif opcion == "2":
                print("[*] Cerrando el sistema...")
                break
            else:
                print("[-] Opción inválida. Elige 1 para analizar.")

    def analizar_cancion(self):
        print("\n" + "="*60)
        print("   EJECUTANDO ANÁLISIS UNIFICADO DE LOS 4 STEMS...")
        print("="*60)
        
        print("\nProcesando Batería (BPM, Golpes y Ritmo)...")
        analizador_perc = AnalizadorPercusion(self.stems["bateria"])
        bpm, tiempos = analizador_perc.extraer_bpm_y_golpes()
        sec_bateria = analizador_perc.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_bat, traductor_bat = None, None
        if sec_bateria:
            traductor_bat = PreprocesadorSimbolico(numero_estados=3)
            cadena_bat = traductor_bat.transformar_a_simbolos(sec_bateria)

        print("\nProcesando Voz (Energía RMS y Textura ZCR)...")
        analizador_v = AnalizadorVoz(self.stems["voz"])
        sec_voz = analizador_v.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_voz, traductor_voz = None, None
        if sec_voz:
            traductor_voz = PreprocesadorSimbolico(numero_estados=3)
            traductor_voz.alfabeto = ['X', 'Y', 'Z']
            cadena_voz = traductor_voz.transformar_a_simbolos(sec_voz)

        print("\nProcesando Bajo (Frecuencia pYIN F0 y Energía)...")
        analizador_b = AnalizadorBajo(self.stems["bajo"])
        sec_bajo = analizador_b.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_bajo, traductor_bajo = None, None
        if sec_bajo:
            traductor_bajo = PreprocesadorSimbolico(numero_estados=3)
            traductor_bajo.alfabeto = ['B1', 'B2', 'B3']
            cadena_bajo = traductor_bajo.transformar_a_simbolos(sec_bajo)

        print("\nProcesando Otros Instrumentos (MFCC_1 y Centroide Espectral)...")
        analizador_o = AnalizadorOtros(self.stems["otros"])
        sec_otros = analizador_o.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_otros, traductor_otros = None, None
        if sec_otros:
            traductor_otros = PreprocesadorSimbolico(numero_estados=3)
            traductor_otros.alfabeto = ['O1', 'O2', 'O3']
            cadena_otros = traductor_otros.transformar_a_simbolos(sec_otros)

        self.resultados_analisis = {
            "bateria": {
                "bpm": bpm,
                "total_golpes": len(tiempos),
                "cadena": cadena_bat,
                "secuencia": sec_bateria,
                "traductor": traductor_bat
            },
            "voz": {
                "cadena": cadena_voz,
                "secuencia": sec_voz,
                "traductor": traductor_voz
            },
            "bajo": {
                "cadena": cadena_bajo,
                "secuencia": sec_bajo,
                "traductor": traductor_bajo
            },
            "otros": {
                "cadena": cadena_otros,
                "secuencia": sec_otros,
                "traductor": traductor_otros
            }
        }
        
        print("\n[+] ¡Análisis unificado completado con éxito!")

    def menu_consultas(self):
        while True:
            print("\n" + "="*50)
            print("CONSULTA Y CLASIFICACIÓN HMM")
            print("="*50)
            print("1. Ver análisis de BATERÍA")
            print("2. Ver análisis de VOZ")
            print("3. Ver análisis de BAJO")
            print("4. Ver análisis de OTROS INSTRUMENTOS")
            print("5. Ver RESUMEN GENERAL (Sintaxis de los 4 stems)")
            print("6. Clasificar Género de la Canción con HMM")
            print("7. Guardar análisis en la Base de Datos")
            print("8. Deshacer último registro en la BD")
            print("9. Salir / Cargar otra canción")
            print("="*50)
            
            opcion = input("[>] Selecciona una opción (1-9): ")
            
            if opcion == "1":
                self._ver_detalle_instrumento("bateria")
            elif opcion == "2":
                self._ver_detalle_instrumento("voz")
            elif opcion == "3":
                self._ver_detalle_instrumento("bajo")
            elif opcion == "4":
                self._ver_detalle_instrumento("otros")
            elif opcion == "5":
                self.resumen()
            elif opcion == "6":
                self.clasificar_hmm()
            elif opcion == "7":
                self.guardar_en_bd()
            elif opcion == "8":
                db = GestorBaseDatos()
                db.borrar_ultimo_registro()
            elif opcion == "9":
                print("Saliendo del menú de consulta...")
                break
            else:
                print("Opción inválida. Intenta nuevamente.")

    def _ver_detalle_instrumento(self, clave):
        datos = self.resultados_analisis[clave]
        
        print(f"\n--- DETALLE DEL ANÁLISIS DE: {clave.upper()} ---")
        if clave == "bateria":
            print(f"BPM Promedio: {datos['bpm']:.2f}")
            print(f"Total de golpes: {datos['total_golpes']}")
            
        print(f"Cadena Simbólica: {datos['cadena']}")
        
        if datos["secuencia"] and datos["traductor"]:
            datos["traductor"].mostrar_calculos_probabilidad(datos["secuencia"])
            datos["traductor"].graficar_y_explicar_clusters(datos["secuencia"])

    def resumen(self):
        print("\n" + "="*60)
        print("  SINTAXIS MULTICHANNEL COMPLETA DE LA CANCIÓN (GMM)")
        print("="*60)
        print(f"BATERÍA : {self.resultados_analisis['bateria']['cadena']}")
        print(f"VOZ     : {self.resultados_analisis['voz']['cadena']}")
        print(f"BAJO    : {self.resultados_analisis['bajo']['cadena']}")
        print(f"OTROS   : {self.resultados_analisis['otros']['cadena']}")
        print("="*60)

    def clasificar_hmm(self):
        print("\n" + "="*60)
        print("   CLASIFICACIÓN DE GÉNERO MEDIANTE HMM (LOG-LIKELIHOOD)")
        print("="*60)
        
        db = GestorBaseDatos()
        registros = db.obtener_secuencias_entrenamiento()
        
        if not registros:
            print("[-] No hay registros almacenados en la base de datos para entrenar el HMM.")
            print("    Por favor, guarda primero varias canciones clasificadas usando la opción 7.")
            return

        clasificador_hmm = ClasificadorEstructuraHMM(numero_estados_ocultos=3)
        clasificador_hmm.entrenar_modelos(registros)

        bateria = self.resultados_analisis["bateria"]["cadena"]
        voz = self.resultados_analisis["voz"]["cadena"]
        bajo = self.resultados_analisis["bajo"]["cadena"]
        otros = self.resultados_analisis["otros"]["cadena"]

        genero, probabilidades = clasificador_hmm.predecir_genero(bateria, voz, bajo, otros)
        self.genero_predicho_hmm = genero

        print("\n--- RESULTADOS DE VEROSIMILITUD POR GÉNERO ---")
        for g, score in probabilidades.items():
            print(f"  • Género '{g}': Log-Likelihood = {score:.4f}")
            
        print(f"\n[+] GÉNERO PREDICHO POR EL SISTEMA HMM: >> {genero.upper()} <<")

    def guardar_en_bd(self):
        sugerencia = f" [{self.genero_predicho_hmm}]" if self.genero_predicho_hmm else ""
        genero_input = input(f"[>] Ingresa el género de la canción{sugerencia}: ").strip()
        
        if not genero_input and self.genero_predicho_hmm:
            genero = self.genero_predicho_hmm
        else:
            genero = genero_input if genero_input else "Desconocido"

        db = GestorBaseDatos()
        
        if self.nombre_pista_actual:
            nombre_cancion = os.path.splitext(self.nombre_pista_actual)[0]
        else:
            nombre_cancion = "Pista_Desconocida"
        
        bat = self.resultados_analisis["bateria"]
        voz = self.resultados_analisis["voz"]
        bajo = self.resultados_analisis["bajo"]
        otros = self.resultados_analisis["otros"]
        
        db.guardar_registro(
            nombre_pista=nombre_cancion, 
            bpm=bat["bpm"], 
            golpes=bat["total_golpes"], 
            cadena_bateria=bat["cadena"],
            cadena_voz=voz["cadena"],
            cadena_bajo=bajo["cadena"],
            cadena_otros=otros["cadena"],
            genero=genero
        )

if __name__ == "__main__":
    app = AplicacionCLI()
    app.iniciar()