import csv
import os


def cargar_telemetria(ruta_archivo: str) -> list[dict]:
    """Carga y valida el dataset de telemetría desde un archivo CSV.
 
    Args:
        ruta_archivo (str): ruta del archivo CSV.

    Returns:
        list[dict]: una lista de diccionarios.

    Raises:
        FileNotFoundError: si el archivo no existe.
        ValueError: Si el archivo está vacío, no contiene registros o tiene datos inválidos.
    """
    if not os.path.exists(ruta_archivo): 
        raise FileNotFoundError(f"No se encontró el archivo: '{ruta_archivo}'")
    
    if os.path.getsize(ruta_archivo) == 0:
        raise ValueError(f"El archivo '{ruta_archivo}' está completamente vacío.")
    
    sesiones = [] # creo la lista vacia

    with open(ruta_archivo, "r", encoding="utf-8", newline="") as file: # newline= Hace que el modulo csv maneje los saltos de linea! 
        lector = csv.DictReader(file)

        for fila in lector:
            try:
                sesion = {
                    "id_sesion": int(fila["id_sesion"]),
                    "servidor": fila["servidor"],
                    "jugador_id": fila["jugador_id"],
                    "tipo_partida": fila["tipo_partida"],
                    "ping_promedio": int(fila["ping_promedio"]),
                    "fps_promedio": int(fila["fps_promedio"]),
                    "duracion_minutos": float(fila["duracion_minutos"]),
                    "intentos_fallidos": int(fila["intentos_fallidos"]),
                    "reportes_trampa": int(fila["reportes_trampa"]),

                }
                sesiones.append(sesion)
            except(ValueError, KeyError, TypeError) as error:
                raise ValueError(f"Error de datos en la línea {lector.line_num}: "
                                 f"Revise si hay valores faltantes o formatos incorrectos. Error: {error}"
                ) from error
            
    if not sesiones:
        raise ValueError("El archivo CSV contiene la cabecera pero no contiene registros.")

    return sesiones