import os
from modulos.separador import MotorSeparacion
from modulos.analizador import AnalizadorPercusion
from modulos.voz import AnalizadorVoz
from modulos.bajo import AnalizadorBajo
from modulos.otros import AnalizadorOtros
from modulos.simbolico import PreprocesadorSimbolico
from modulos.database import GestorBaseDatos

class AplicacionCLI:
    def __init__(self):
        self.separador = MotorSeparacion()
        self.stems = None
        self.resultados_analisis = None

    def iniciar(self):
        print("="*60)
        print("   SISTEMA DE RECONOCIMIENTO DE PATRONES MUSICALES (POO)")
        print("="*60)
        
        cancion = input("[>] Ingresa la ruta de tu pista .mp3: ")
        
        try:
            self.stems = self.separador.procesar_pista(cancion)
        except FileNotFoundError as e:
            print(f"[-] Error: {e}")
            return

        if self.stems:
            self._menu_procesamiento_inicial()

    def _menu_procesamiento_inicial(self):
        while True:
            print("\n" + "="*50)
            print("        FASE 1: PROCESAMIENTO Y ANÁLISIS")
            print("="*50)
            print("1. Analizar Canción Completa (Batería, Voz, Bajo y Otros)")
            print("2. Salir")
            print("="*50)
            
            opcion = input("[>] Elige una opción: ")
            
            if opcion == "1":
                self._analizar_cancion_completa()
                self._menu_consulta_resultados()
                break
            elif opcion == "2":
                print("[*] Cerrando el sistema...")
                break
            else:
                print("[-] Opción inválida. Elige 1 para analizar.")

    def _analizar_cancion_completa(self):
        print("\n" + "="*60)
        print("   EJECUTANDO ANÁLISIS UNIFICADO DE LOS 4 STEMS...")
        print("="*60)
        
        print("\n[1/4] Procesando Batería (BPM, Golpes y Ritmo)...")
        analizador_perc = AnalizadorPercusion(self.stems["bateria"])
        bpm, tiempos = analizador_perc.extraer_bpm_y_golpes()
        sec_bateria = analizador_perc.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_bat, traductor_bat = None, None
        if sec_bateria:
            traductor_bat = PreprocesadorSimbolico(numero_estados=3)
            cadena_bat = traductor_bat.transformar_a_simbolos(sec_bateria)

        print("\n[2/4] Procesando Voz (Energía RMS y Textura ZCR)...")
        analizador_v = AnalizadorVoz(self.stems["voz"])
        sec_voz = analizador_v.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_voz, traductor_voz = None, None
        if sec_voz:
            traductor_voz = PreprocesadorSimbolico(numero_estados=3)
            traductor_voz.alfabeto = ['X', 'Y', 'Z']
            cadena_voz = traductor_voz.transformar_a_simbolos(sec_voz)

        print("\n[3/4] Procesando Bajo (Frecuencia pYIN F0 y Energía)...")
        analizador_b = AnalizadorBajo(self.stems["bajo"])
        sec_bajo = analizador_b.extraer_secuencia_temporal(ventana_segundos=10)
        
        cadena_bajo, traductor_bajo = None, None
        if sec_bajo:
            traductor_bajo = PreprocesadorSimbolico(numero_estados=3)
            traductor_bajo.alfabeto = ['B1', 'B2', 'B3']
            cadena_bajo = traductor_bajo.transformar_a_simbolos(sec_bajo)

        print("\n[4/4] Procesando Otros Instrumentos (MFCC_1 y Centroide Espectral)...")
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

    def _menu_consulta_resultados(self):
        while True:
            print("\n" + "="*50)
            print("        FASE 2: CONSULTA DE RESULTADOS")
            print("="*50)
            print("1. Ver análisis de BATERÍA")
            print("2. Ver análisis de VOZ")
            print("3. Ver análisis de BAJO")
            print("4. Ver análisis de OTROS INSTRUMENTOS")
            print("5. Ver RESUMEN GENERAL (Sintaxis de los 4 stems)")
            print("6. Guardar análisis en la Base de Datos")
            print("7. Deshacer último registro en la BD")
            print("8. Salir / Cargar otra canción")
            print("="*50)
            
            opcion = input("[>] Selecciona el análisis que deseas ver (1-8): ")
            
            if opcion == "1":
                self._ver_detalle_instrumento("bateria")
            elif opcion == "2":
                self._ver_detalle_instrumento("voz")
            elif opcion == "3":
                self._ver_detalle_instrumento("bajo")
            elif opcion == "4":
                self._ver_detalle_instrumento("otros")
            elif opcion == "5":
                self._ver_resumen_general()
            elif opcion == "6":
                self._guardar_en_bd()
            elif opcion == "7":
                db = GestorBaseDatos()
                db.borrar_ultimo_registro()
            elif opcion == "8":
                print("[*] Saliendo del menú de consulta...")
                break
            else:
                print("[-] Opción inválida. Intenta nuevamente.")

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

    def _ver_resumen_general(self):
        print("\n" + "="*60)
        print("   SINTAXIS MULTICHANNEL COMPLETA DE LA CANCIÓN (GMM)")
        print("="*60)
        print(f"BATERÍA : {self.resultados_analisis['bateria']['cadena']}")
        print(f"VOZ     : {self.resultados_analisis['voz']['cadena']}")
        print(f"BAJO    : {self.resultados_analisis['bajo']['cadena']}")
        print(f"OTROS   : {self.resultados_analisis['otros']['cadena']}")
        print("="*60)

    def _guardar_en_bd(self):
        genero = input("[>] Ingresa el género real de la canción (Ej. Rock, Pop, Electronica): ")
        db = GestorBaseDatos()
        nombre_cancion = os.path.basename(self.separador.ruta_salida)
        
        bat = self.resultados_analisis["bateria"]
        voz = self.resultados_analisis["voz"]
        bajo = self.resultados_analisis["bajo"]
        otros = self.resultados_analisis["otros"]
        
        db.guardar_registro(
            nombre_cancion, 
            bat["bpm"], 
            bat["total_golpes"], 
            bat["cadena"],       
            voz["cadena"],
            bajo["cadena"],
            otros["cadena"],
            genero
        )
if __name__ == "__main__":
    app = AplicacionCLI()
    app.iniciar()