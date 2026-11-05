def calcular_porcentaje(valor: int, total: int) -> float:
    """Calcula que porcentaje representa una cantidad sobre el total.

    Args:
       valor  (int): valor que se quiere expresar como porcentaje.
       total (int): cantidad total de referencia.

    Returns:
        float: porcentaje redondeado a 2 decimales (0.0 si el total es 0). 
    """
    if total == 0:
        return 0.0
    return round(( valor / total) * 100, 2)


def calcular_promedio(suma: float, cantidad: int) -> float:
    """Calcula el promedio de una suma, redondeando a dos decimales.

    Args:
       suma  (float): suma acumulada de los valores.
       cantidad (int): cantidad de valores sumados.

    Returns:
        float: promedio redondeado a 2 decimales (0.0 si cantidad es 0). 
    """
    if cantidad == 0:
        return 0.0
    return round(suma / cantidad, 2)


def calcular_estadisticas_globales(sesiones: list[dict]) -> dict:
    """Calcula las métricas globales de todas las sesiones registradas de telemetría.

    Args:
        sesiones (list[dict]): sesiones de telemetría cargadas.

    Returns:
        dict: total de sesiones, ping promedio, duración promedio y porcentaje de partidas
        competitivas (todo en cero si la lista está vacía).    
    """
    total = len(sesiones)
    if total == 0:
        return {
            "total_sesiones": 0,
            "ping_promedio": 0.0,
            "duracion_promedio": 0.0,
            "porcentaje_competitivas": 0.0
        }
    
    suma_ping = 0
    suma_duracion = 0
    competitivas = 0
    for sesion in sesiones:
        suma_ping += sesion["ping_promedio"]
        suma_duracion += sesion["duracion_minutos"]
        if sesion["tipo_partida"] == "Competitiva" or sesion["tipo_partida"] == "Torneo":
            competitivas += 1
    
    return {
        "total_sesiones": total,
        "ping_promedio": calcular_promedio(suma_ping, total),
        "duracion_promedio": calcular_promedio(suma_duracion, total),
        "porcentaje_competitivas": calcular_porcentaje(competitivas, total)
    }


def analizar_por_servidor(sesiones: list[dict]) -> dict:
    """Agrupa las sesiones por región del servidor usando un diccionario acumulador.

    Args: 
        sesiones (list[dict]): sesiones de telemetría cargadas.

    Returns:
        dict: por cada servidor, la cantidad de sesiones, el ping promedio y los FPS promedio.
    """
    acumulador = {} # Diccionario vacío para guardar las sumas y cantidades por servidor, seran usadas para calcular los promedios.

    for sesion in sesiones:
        nombre = sesion["servidor"]
        if nombre not in acumulador:
            acumulador[nombre] = {"cantidad": 0, "suma_ping": 0, "suma_fps": 0}
        acumulador[nombre]["cantidad"] += 1
        acumulador[nombre]["suma_ping"] += sesion["ping_promedio"]
        acumulador[nombre]["suma_fps"] += sesion["fps_promedio"]

    resultado = {} # Diccionario vacio para guardar los promedios por servidor.
 
    for nombre, datos in acumulador.items():
        resultado[nombre] = {
            "cantidad": datos["cantidad"],
            "ping_promedio": calcular_promedio(datos["suma_ping"], datos["cantidad"]),
            "fps_promedio": calcular_promedio(datos["suma_fps"], datos["cantidad"])
        }

    return resultado


def clasificar_incidentes(sesiones: list[dict]) -> tuple[dict, list[dict]]:
    """Clasifica cada sesión como Normal, Sospechoso o Crítico según reglas Heurísticas.
    
    Args:
        sesiones (list[dict]): sesiones de telemetría cargadas.

    Returns: 
        tuple[dict, list[dict]]: diccionario de frecuencias por estado y lista de sesiones críticas detectadas.    
    """

    # umbrales de alerta: para cambiar un criterio se modifica un solo valor.
    umbral_trampas = 3
    umbral_intentos = 4
    umbral_ping = 200
    umbral_intentos_sospechosos = 2
    reportes_sospechoso = 2
    criticos = [] # Inicializo la lista de sesiones críticas
    resumen = { 
        "Normal": 0,
        "Sospechoso": 0,
        "Crítico": 0
    }

    for sesion in sesiones:
        # Con estas dos variables se puede evaluar una sola vez cada condición "Crítica".
        por_trampas = sesion["reportes_trampa"] >= umbral_trampas
        por_intentos = sesion["intentos_fallidos"] >= umbral_intentos

        if por_trampas or por_intentos:
            resumen["Crítico"] += 1

            if por_trampas and por_intentos:
                motivo = f"Exceso de reportes por trampa ({sesion['reportes_trampa']}) e intentos fallidos ({sesion['intentos_fallidos']})"
            elif por_trampas:
                motivo = f"Exceso de reportes por trampa ({sesion['reportes_trampa']})"
            else:
                motivo = f"Ataque de fuerza bruta en login ({sesion['intentos_fallidos']} intentos fallidos)"

            criticos.append({
                "id_sesion": sesion["id_sesion"],
                "jugador_id": sesion["jugador_id"],
                "servidor": sesion["servidor"],
                "motivo": motivo
            })

        elif (sesion["ping_promedio"] > umbral_ping and sesion["intentos_fallidos"] >= umbral_intentos_sospechosos) or sesion["reportes_trampa"] == reportes_sospechoso:
            resumen["Sospechoso"] += 1
        else:
            resumen["Normal"] += 1

    return resumen, criticos