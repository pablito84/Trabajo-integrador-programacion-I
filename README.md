# GameSec Monitor \- Telemetría de Servidores de Videojuegos

**Trabajo Práctico integrador \- Taller de Programación I** **Universidad Nacional de Hurlingham \- Instituto de Tecnología e Ingeniería**

La redacción de las conclusiones y la revisión final del formato del reporte fueron trabajadas en conjunto por todo el equipo.

## Integrantes

| Nombre y Apellido | DNI | Carrera |
| :---- | :---- | :---- |
| Pablo Mateo             | 30.930.326 | Tecnicatura en Inteligencia Artificial |
| Gonzalo Ruiz            | 45.202.061 | Tecnicatura en Inteligencia Artificial |
| Ignacio Delgado Cremona | 40.361.125 | Tecnicatura en Inteligencia Artificial |
| Román Jaime             | 43.735.244 | Tecnicatura en Inteligencia Artificial |

Descripción

Herramienta de consola que procesa archivos de telemetría de servidores de videojuegos multijugador, calcula métricas operativas por región y clasifica automáticamente las sesiones anómalas mediante un motor de reglas determinísticas.

El sistema modela cada sesión como un diccionario y el dataset completo como una lista de diccionarios, usando estructuras nativas de Python.

## Requisitos

- Python 3.10 o superior  
- Sin dependencias externas. Se usan únicamente módulos de la librería estándar:  
  - `csv`: Lectura del dataset  
  - `os`: Rutas y validación  
  - `datetime`: Fecha del reporte

### Verificar que Python esté instalado

Abrir una consola y ejecutar:

```
python --version
```

En Windows, si ese comando no responde probar con:

```
py --version
```

La respuesta esperada es `Python 3.10.x` o superior.

### Si no está instalado o la versión es anterior a 3.10

1. Descargar el instalador desde: [https\://www\.python.org/downloads/](https://www.python.org/downloads/)  
2. **En Windows, tildar la casilla "Add Python to PATH"** en la primera pantalla del instalador. Este paso es importante ya que si no se hace, la consola no reconoce el comando `python`.  
3. Cerrar y volver a abrir la consola, y verificar nuevamente con `python --version`.

## Ejecución

1. Verificar que `gamesec_logs.csv` esté en la carpeta `data/`.  
2. Desde la raíz del proyecto, ejecutar:

```
cd src
python main.py
```

3. En el menú elegir la opción `1` para cargar el dataset antes de usar las opciones que van del 2 a 5\.  
4. La opción `5` genera `output/reporte_gamesec.txt` con el informe consolidado.

El programa resuelve la ruta del dataset a partir de la ubicación de main.py, por lo que también puede ejecutarse desde la raíz del proyecto con python src/main.py

## Estructura del proyecto

```
TP Integrador/
├── README.md
├── data/
│   └── gamesec_logs.csv       Dataset de 150 sesiones provisto por la cátedra
├── output/
│   └── reporte_gamesec.txt    Reporte generado por la opción 5 del menú
└── src/
    ├── carga.py               Lectura, tipado y validación del CSV
    ├── procesamiento.py       Métricas, agrupamiento y clasificación de incidentes
    ├── reporte.py             Formateo de texto y exportación del reporte            
    └── main.py                Menú de consola
```

## Responsabilidad de cada módulo

- **carga.py**: lee el csv, convierte los tipos y valida el archivo.  
- **procesamiento.py**: cálculo puro, sin texto ni formato.  
- **reporte.py**: arma el texto de tablas y secciones, y genera el archivo del reporte.  
- **main.py**: menú interactivo, solamente coordina a los otros módulos.

## Menú de opciones

1. **Cargar y validar dataset**: Ejecuta la función cargar\_telemetria() \- Lee el CSV, castea los tipos y valida el archivo.  
2. **Ver estadísticas globales de servidores**: Ejecuta la función calcular\_estadisticas\_globales() \- Muestra total, ping promedio, duración media y porcentaje de alta competencia  
3. **Ver rendimiento por región de servidor**: Ejecuta la función analizar\_por\_servidor() \- Muestra la tabla de sesiones, ping y FPS por región.  
4. **Auditar incidentes de seguridad** (Críticos y Sospechosos): Ejecuta la función clasificar\_incidentes() \- Muestra la distribución de estados y el detalle de sesiones críticas  
5. **Exportar reporte consolidado** (reporte\_gamesec.txt): Ejecuta la función exportar\_reporte() ubicada en reporte.py \- Genera "reporte\_gamesec.txt" con los cuatro bloques del informe  
6. **Salir**: Finaliza ejecución del programa

Las opciones 2 a 5 requieren haber cargado el dataset previamente con la opción 1\.

## Motor heurístico de clasificación

Implementado en la función clasificar\_incidentes(), las reglas se evalúan en orden:

- **Crítico**: reportes\_trampa \>= 3 o intentos\_fallidos \>= 4  
- **Sospechoso**: si no es crítico y cumple `(ping_promedio > 200 y intentos_fallidos >= 2)` o `(reportes_trampa == 2)`  
- **Normal**: Cualquier sesión que no sea de las anteriores

Los umbrales están definidos como variables locales al inicio de clasificar\_incidentes(), de modo que modificar un criterio de alerta requiere cambiar un único valor.

Cada sesión crítica genera un motivo descriptivo según la causa detectada: exceso de reportes por trampa, fuerza bruta en el login o la combinación de ambos.

## Resultados obtenidos

Sobre el dataset provisto (150 sesiones):

| Métrica global | Valor |
| :---- | :---- |
| Ping promedio | 148.44 ms |
| Duración media de partida | 29.39 min |
| Partidas de alta competencia | 53.33% |

&nbsp;

| Servidor | Sesiones | Ping promedio | FPS promedio |
| :---- | :---- | :---- | :---- |
| SA-BuenosAires | 39 | 78.95 ms | 90.85 fps |
| EU-Frankfurt | 42 | 199.07 ms | 96.71 fps |
| NA-Virginia | 39 | 228.31 ms | 91.08 fps |
| SA-SaoPaulo | 30 | 64.07 ms | 84.60 fps |

&nbsp;

| Estado de seguridad | Sesiones | Porcentaje |
| :---- | :---- | :---- |
| Normal | 118 | 78.67% |
| Sospechoso | 22 | 14.67% |
| Crítico | 10 | 6.67% |

## Decisiones de diseño

- **Diccionario acumulador dinámico**: analizar\_por\_servidor(): descubre las regiones a medida que aparecen en el archivo, sin listas prefijadas. Si el dataset incorpora un servidor nuevo, el reporte lo incluye sin tocar el código.

- **Separación de acumulación y cálculo**: primero se acumulan sumas y cantidades, y recién en un segundo recorrido se calculan los promedios, así se evita recalcular divisiones en cada iteración.

- **Funciones puras sin estado compartido**: Ninguna función usa variables globales: todas reciben los datos por parámetro y devuelven el resultado con return. main() es la única que mantiene el estado de la sesión, en una variable local.

- **Validación temprana en la carga**: cargar\_telemetria() verifica la existencia del archivo antes de abrirlo y que contenga al menos un registro antes de retornar, lanzando FileNotFoundError o ValueError según el caso. main() captura ambas y muestra un mensaje legible en lugar de un traceback.

- **Protección ante dataset vacío**: calcular\_estadisticas\_globales() retorna las métricas en cero si recibe una lista vacía, evitando una división por cero aunque se la invoque de forma aislada.

- **Rutas relativas al archivo fuente**: Las rutas se construyen con os.path.dirname(**file**) en lugar de rutas relativas al directorio de trabajo, para que el programa funcione sin importar desde dónde se lo ejecute.

- **Formato separado del cálculo**: las funciones formatear\_\* y armar\_\* de reporte.py devuelven texto (str). Así el mismo formato sirve para mostrar por pantalla menú y para escribir el archivo sin duplicar código.

- **Cálculo de porcentaje centralizado**: calcular\_porcentaje() concentra la fórmula y la protección contra división por cero.