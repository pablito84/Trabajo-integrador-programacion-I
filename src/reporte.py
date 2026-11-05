from datetime import datetime

from procesamiento import (  
    calcular_estadisticas_globales,
    calcular_porcentaje,
    analizar_por_servidor, 
    clasificar_incidentes,
)


# Formateo
def linea(caracter: str = "-", largo: int = 70) -> str:
    """Genera una línea de separación.
     
    Args:
        caracter (str): el caracter que se repetirá para formar la línea. 
        largo (int): el largo de la línea.

    Returns:
        str: una línea de separación formada por el caracter repetido.
    """
    return caracter * largo


def formatear_tabla_servidores(rendimiento: dict, separador: str = "") -> str:
    """Genera una tabla de rendimiento por servidor en formato de texto.

    Args:
        rendimiento (dict): diccionario con el rendimiento por servidor.
        separador (str): Linea que se agrega debajo del encabezado de la tabla; si está vacío, no se agrega.

    Returns:
        str: tabla de rendimiento por servidor en formato de texto.
    """
    lineas = [f"{'Servidor':<18} | {'Sesiones':<8} | {'Ping Promedio':<13} | {'FPS Promedio'}"]
    if separador:
        lineas.append(separador)

    for servidor, datos in rendimiento.items():
        ping = f"{datos['ping_promedio']:.2f} ms"
        fps = f"{datos['fps_promedio']:.2f} fps"
        lineas.append(f"{servidor:<18} | {datos['cantidad']:<8} | {ping:<13} | {fps}")

    return "\n".join(lineas)


def formatear_estadisticas(estadisticas: dict) -> str:
    """Genera un resumen de estadísticas globales en formato de texto.

    Args:
        estadisticas (dict): diccionario con las estadísticas globales.

    Returns:
        str: resumen de estadísticas globales en formato de texto.
    """
    return (
        f"Total de sesiones procesadas: {estadisticas['total_sesiones']}\n"
        f"Ping promedio global: {estadisticas['ping_promedio']:.2f} ms\n"
        f"Duración media de partida: {estadisticas['duracion_promedio']:.2f} min\n"
        f"Partidas de alta competencia (Ranked/Torneo): {estadisticas['porcentaje_competitivas']:.2f}%"
    )


def formatear_distribucion(resumen: dict, total: int) -> str:
    """Genera un resumen de la distribución de incidentes en formato de texto.

    Args:
        resumen (dict): diccionario con el conteo de incidentes por categoría.
        total (int): total de sesiones procesadas.

    Returns:
        str: resumen de la distribución de incidentes en formato de texto.
    """
    lineas = []
    for estado, etiqueta in [("Normal", "Normales:"), ("Sospechoso", "Sospechosos:"), ("Crítico", "Críticos:")]:
        cantidad = resumen[estado]
        porcentaje = calcular_porcentaje(cantidad, total)
        lineas.append(f"  • {etiqueta:<13}{cantidad:>3} sesiones ({porcentaje:5.2f}%)")
    return "\n".join(lineas)


def formatear_criticos(criticos: list[dict]) -> str:
    """Genera el detalle de las sesiones críticas en formato de texto.

    Args:
        criticos (list[dict]): sesiones críticas con id_sesion, jugador_id, servidor y motivo.   

    Returns:
        str: detalle de las sesiiones críticas en formato de texto
    """
    lineas = []

    for critico in criticos:
        lineas.append(f"  [!] Sesión #{critico['id_sesion']:<3} | Jugador: {critico['jugador_id']} | Servidor: {critico['servidor']}")
        lineas.append(f"      Motivo: {critico['motivo']}")

    return "\n".join(lineas)


# Bloques del reporte
def obtener_conclusiones() -> list[str]:
    """Devuelve las conclusiones técnicas redactadas por el grupo.
    
    Returns: 
        list[str]: conclusiones tecncicas, una por cada área de análisis.
    """
    return ["Calidad de servicio (Videojuegos): El cuello de botella de la experiencia de juego está en la infraestructura de red, no en el"
                        " equipo del jugador: Mientras el ping promedio varía 3.5 veces entre regiones (64.07 ms en SA-SaoPaulo contra 228.31 ms en NA-Virginia), los FPS se mantienen homogéneos en todas ellas (entre 84.60 y 96.71)."
                        " Dado que el 53.33% de las sesiones corresponde a modalidades Competitiva o Torneo, la latencia de las regiones del hemisferio norte compromete directamente la jugabilidad donde más impacta."
                   ,"Detección de incidentes (Ciberseguridad): Las dos condiciones del nivel Crítico no identifican poblaciones independientes: las 10 sesiones críticas detectadas cumplen"
                        " simultáneamente el umbral de reportes por trampa (≥ 3) y el de intentos fallidos de autenticación (≥ 4)."
                        " Esta coincidencia total sugiere un único patrón de comportamiento —compatible con cuentas comprometidas o con uso de"
                        " herramientas automatizadas— antes que dos amenazas distintas, y justificaría evaluar una regla combinada con umbrales"
                        " más bajos para detectar casos tempranos."
                   ,"Modelado de datos (IA - Datos): El clasificador por reglas procesa las 150 sesiones sin intervención manual y produce un dataset etiquetado en"
                        " tres clases (118 normales, 22 sospechosas y 10 críticas), apto como insumo para entrenar un modelo supervisado."
                        " Su limitación es que los umbrales responden a criterios de negocio y no a la distribución observada: el corte de reportes por"
                        " trampa está fijado en 3, valor que no aparece en ninguna sesión del dataset. Un modelo entrenado sobre estos datos podría ajustar"
                        " esos cortes de forma empírica."
                    ]  # Lista de conclusiones técnicas.


def armar_encabezado() -> str:
    """Arma el encabezado del reporte con el título y la fecha de generación.

    Returns:
        str: encabezado del reporte en formato de texto.
    """
    fecha = datetime.now().strftime("%d/%m/%Y")
    return (
        linea('=') + "\n"
        + "REPORTE DE AUDITORÍA Y TELEMETRÍA — GAMESEC".center(70) + "\n"
        + linea('=') + "\n"
        + f"Fecha de generación: {fecha}\n"
    )


def armar_seccion_resumen(estadisticas: dict) -> str:
    """Arma la seccion #1 del reporte: Resumen global operativo

    Args:
        estadisticas (dict): diccionario de las estadisticas globales.

    Returns:
        str: sección del reporte en formato de texto.
    """
    return (
        "\n[1] RESUMEN GLOBAL OPERATIVO\n"
        + linea() + "\n"
        + formatear_estadisticas(estadisticas) + "\n"
    )


def armar_seccion_servidores(rendimiento: dict) -> str:
    """Arma la seccion #2 del reporte: Rendimiento regional por servidor.

    Args:
        rendimiento (dict): diccionario con el rendimiento por servidor.

    Returns:
        str: sección del reporte en formato de texto.
    """
    return (
        "\n[2] RENDIMIENTO REGIONAL POR SERVIDOR\n"
        + linea() + "\n"
        + formatear_tabla_servidores(rendimiento, separador=linea()) + "\n"
    )


def armar_seccion_incidentes(resumen: dict, criticos: list[dict], total: int) -> str:
    """Arma la seccion #3 del reporte: Auditoria de seguridad e incidentes.

    Args:
        resumen (dict): diccionario con el conteo de sesiones por estado.
        criticos (list[dict]): lista de sesiones criticas detectadas.
        total (int): total de sesiones procesadas.

    Returns:
        str: sección del reporte en formato de texto.
    """
    return (
        "\n[3] AUDITORÍA DE SEGURIDAD E INCIDENTES\n"
        + linea() + "\n"
        + "Distribución de estados de seguridad:\n"
        + formatear_distribucion(resumen, total) + "\n\n"
        + "Detalle de Sesiones Críticas Detectadas:\n"
        + formatear_criticos(criticos) + "\n"
    )


def armar_seccion_conclusiones(conclusiones: list[str]) -> str:
    """Arma la seccion #4 del reporte: conclusiones tecnicas del equipo.

    Args:
        conclusiones (list[str]): conclusiones que se numeran en el reporte.

    Returns:
        str: sección del reporte en formato de texto
    """    
    texto = "\n".join(f"{indice}. {data}" for indice, data in enumerate(conclusiones, start=1))
    return (
        "\n[4] CONCLUSIONES TÉCNICAS DEL EQUIPO\n"
        + linea() + "\n"
        + texto + "\n"
    )


def armar_pie() -> str:
    """Arma el pie de cierre del reporte.

    Returns:
        str: pie del reporte en formato de texto.
    """   
    return ( 
         linea("=") + "\n"  
         + "FIN DEL REPORTE GAMESEC".center(70) + "\n"   
         + linea("=") + "\n"  
    )


# Exportación

def exportar_reporte(sesiones: list[dict], ruta_salida: str = "reporte_gamesec.txt") -> None:
    """Genera el reporte consolidado de auditoría en un archivo de texto.
    
    Args: 
        sesiones (list[dict]): sesiones de telemetria ya cargadas.
        ruta_salida (str): ruta del archivo de texto que se genera.

    Raises: 
        OSError: Si no se puede escribir el archivo.    
    """
    estadisticas = calcular_estadisticas_globales(sesiones)
    rendimiento = analizar_por_servidor(sesiones)
    resumen, criticos = clasificar_incidentes(sesiones)
    total = estadisticas["total_sesiones"]

    with open(ruta_salida, "w", encoding="utf-8") as file:
        file.write(armar_encabezado())
        file.write(armar_seccion_resumen(estadisticas))
        file.write(armar_seccion_servidores(rendimiento))
        file.write(armar_seccion_incidentes(resumen, criticos, total))
        file.write(armar_seccion_conclusiones(obtener_conclusiones()))
        file.write(armar_pie())

