import os


from carga import cargar_telemetria

from procesamiento import ( 
    calcular_estadisticas_globales,
    analizar_por_servidor,
    clasificar_incidentes,
)    

from reporte import (
    exportar_reporte,
    formatear_estadisticas,
    formatear_tabla_servidores,
    formatear_distribucion,
    formatear_criticos,
    linea,
)


def mostrar_menu() -> None:
    """Imprime el panel de control."""
    print(linea("="))
    print("      GAMESEC MONITOR - PANEL DE CONTROL")
    print(linea("="))

    print("1. Cargar y validar dataset")
    print("2. Ver estadísticas globales de servidores")
    print("3. Ver rendimiento por región de servidor")
    print("4. Auditar incidentes de seguridad (Críticos y Sospechosos)")
    print("5. Exportar reporte consolidado (reporte_gamesec.txt)")
    print("6. Salir")
    print(linea("="))


def opcion_cargar(ruta_csv: str, sesiones_actuales: list[dict]) -> list[dict]:
    """Carga el CSV; si falla, conserva las sesiones ya cargadas
    
    Args: 
        ruta_csv (str): ruta del archivo CSV.
        sesiones_actuales (list[dict]): sesiones cargadas hasta el momento.

    Returns:
        list[dict]: sesiones recién cargadas, o las actuales si hubo un error.
    """
    try:
        sesiones = cargar_telemetria(ruta_csv)
        print(f"Se han cargado: {len(sesiones)} sesiones de Telemetría.")
        return sesiones
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo '{ruta_csv}'. ")
    except (ValueError, KeyError) as error:
        print(f"Error en los datos: {error}")
    return sesiones_actuales


def opcion_estadisticas(sesiones: list[dict]) -> None:
    """Muestra por pantalla las estadisticas globales.

    Args: 
        sesiones (list[dict]): sesiones de telemetría cargadas.
    """
    print("Estadísticas Globales:")
    print(formatear_estadisticas(calcular_estadisticas_globales(sesiones)))


def opcion_rendimiento(sesiones: list[dict]) -> None:
    """Muestra por pantalla el rendimiento por  servidor.

    Args: 
        sesiones (list[dict]): sesiones de telemetría cargadas.
    """    
    print("Rendimiento por servidor")
    print(formatear_tabla_servidores(analizar_por_servidor(sesiones)))


def opcion_incidentes(sesiones: list[dict]) -> None:
    """Muestra por pantalla la distribución de estados y las sesiones críticas.

    Args: 
        sesiones (list[dict]): sesiones de telemetría cargadas.
    """        
    resumen, criticos = clasificar_incidentes(sesiones)
    print("Incidentes de seguridad:")
    print(formatear_distribucion(resumen, len(sesiones)))
    print("Detalle de sesiones críticas detectadas:")
    print(formatear_criticos(criticos))
    print()


def opcion_exportar(sesiones: list[dict], ruta_reporte: str) -> None:
    """Exporta el reporte consolidado e informa si hubo un error de escritura.

    Args: 
        sesiones (list[dict]): sesiones de telemetria cargadas.
        ruta_reporte (str): ruta del archivo de reporte a generar.
    """    
    try:
        exportar_reporte(sesiones, ruta_reporte)
        print("Reporte generado: reporte_gamesec.txt")
    except OSError as error:
        print(f"Error al generar el reporte: {error} ")


def obtener_rutas() -> tuple[str, str]:
    """Arma las rutas del CSV y del reporte a partir de la ubicacion de este archivo.

    Returns:
        tuple[str, str]: ruta del CSV de telemetria y ruta del reporte a generar.
    """
    carpeta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_csv = os.path.join(carpeta_actual, "..", "data", "gamesec_logs.csv")  # Ruta al archivo CSV de telemetría
    ruta_reporte = os.path.join(carpeta_actual, "..", "output", "reporte_gamesec.txt")

    return ruta_csv, ruta_reporte

def main() -> None:
    """Ejecuta el menu principal y mantiene las sesiones cargadas."""
    sesiones = []  # Inicializo la lista de sesiones vacía
    ruta_csv, ruta_reporte = obtener_rutas()
    
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "6":
            print("Saliendo del programa...")
            break
        elif opcion == "1":
            sesiones = opcion_cargar(ruta_csv, sesiones)
        elif opcion in ("2", "3", "4", "5") and not sesiones:
            print("Primero debe cargar un dataset válido (opción 1).")
        elif opcion == "2":
            opcion_estadisticas(sesiones)
        elif opcion == "3":
            opcion_rendimiento(sesiones)    
        elif opcion == "4":
            opcion_incidentes(sesiones)
        elif opcion == "5":
            opcion_exportar(sesiones, ruta_reporte)
        else:
            print("Opción inválida. Por favor, seleccione una opción válida.")


if __name__ == "__main__":
    main()
 