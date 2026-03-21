# Práctica 2 — Búsqueda Informada

Implementación de los algoritmos **A\*** y **Simulated Annealing** aplicados al 8-puzzle, 15-puzzle y Sudoku, con interfaz gráfica interactiva construida en Tkinter y comparación de rendimiento entre heurísticas y algoritmos.

---

## Contenido

- [Descripción](#descripción)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Algoritmos implementados](#algoritmos-implementados)
- [Heurísticas](#heurísticas)
- [Requisitos](#requisitos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Ejecución con Docker](#ejecución-con-docker)
- [Tests](#tests)
- [GitHub Actions](#github-actions)

---

## Descripción

Esta práctica implementa dos familias de algoritmos de búsqueda inteligente:

- **Búsqueda informada (A\*)**: explora el espacio de estados guiándose por una función `f(n) = g(n) + h(n)`, donde `g(n)` es el costo acumulado desde el inicio y `h(n)` es una estimación heurística del costo restante hasta la meta. Se aplica al 8-puzzle y al 15-puzzle con tres heurísticas distintas y al Sudoku en niveles fácil e intermedio.

- **Búsqueda local (Simulated Annealing)**: mejora iterativamente una solución inicial aceptando soluciones peores con una probabilidad controlada por una temperatura `T` que decrece con el tiempo, permitiendo escapar de óptimos locales. Se aplica al Sudoku en los tres niveles de dificultad.

La interfaz gráfica permite resolver los problemas paso a paso, visualizar el proceso de búsqueda en tiempo real y comparar el rendimiento de los algoritmos mediante tablas de métricas.

---

## Estructura del proyecto

```
practica_2/
├── main.py                        ← Punto de entrada, lanza la app
├── src/
│   ├── __init__.py
│   ├── algorithms/
│   │   ├── __init__.py
│   │   ├── a_star.py              ← Algoritmo A* para N-Puzzle
│   │   ├── annealing.py           ← Simulated Annealing y A* para Sudoku
│   │   └── heuristics.py          ← Fichas fuera de lugar, Manhattan, Conflicto Lineal
│   ├── gui/
│   │   ├── __init__.py
│   │   ├── puzzle_gui.py          ← Interfaz gráfica del 8-puzzle y 15-puzzle
│   │   └── sudoku_gui.py          ← Interfaz gráfica del Sudoku
│   └── utils/
│       ├── __init__.py
│       └── metrics.py             ← Benchmarking y formato de tablas
├── tests/
│   ├── __init__.py
│   ├── test_puzzle.py             ← Tests del A* para puzzle
│   └── test_sudoku.py             ← Tests del A* y SA para Sudoku
├── .github/
│   └── workflows/
│       └── ci.yml                 ← GitHub Actions CI
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

## Algoritmos implementados

### A* — N-Puzzle

El algoritmo A* mantiene una cola de prioridad ordenada por `f(n) = g(n) + h(n)`. En cada iteración extrae el nodo con menor `f`, genera sus vecinos moviendo el espacio vacío en las cuatro direcciones posibles y actualiza sus costos si se encontró un camino más corto. Antes de iniciar la búsqueda verifica si el estado es resoluble contando inversiones. Al terminar devuelve la secuencia de estados, el número de movimientos, los nodos expandidos, el tiempo de ejecución y el pico de memoria.

### A* — Sudoku (backtracking + MRV)

Para el Sudoku, A* se implementa como backtracking con la heurística MRV (Minimum Remaining Values): en cada paso elige la celda vacía con menos valores posibles válidos, lo que reduce drásticamente el espacio de búsqueda. Es viable para los niveles fácil e intermedio.

### Simulated Annealing — Sudoku

Parte de un estado inicial donde cada bloque 3×3 se rellena aleatoriamente con los dígitos faltantes. En cada iteración elige un bloque al azar e intercambia dos celdas no fijas dentro de él. Acepta el nuevo estado si mejora, o con probabilidad `e^(-ΔE/T)` si empeora. La temperatura baja exponencialmente según `T = T × δ`. Cada 10,000 iteraciones sin mejora el algoritmo se reinicia desde un nuevo estado aleatorio para escapar de mínimos locales.

---

## Heurísticas

Las tres heurísticas implementadas son **admisibles**: nunca sobreestiman el costo real, lo que garantiza que A* siempre encuentre la solución óptima.

| Heurística | Descripción | Informatividad |
|---|---|---|
| Fichas fuera de lugar | Cuenta cuántas fichas no están en su posición objetivo | Baja |
| Distancia Manhattan | Suma de distancias horizontal + vertical de cada ficha a su meta | Media |
| Conflicto Lineal | Manhattan + 2 por cada par de fichas en conflicto en la misma fila/columna | Alta |

---

## Requisitos

- Python 3.10 o superior
- Tkinter (incluido en Python; en Ubuntu instalar con `sudo apt-get install python3-tk`)
- pytest y pytest-cov (ver `requirements.txt`)

---

## Instalación y ejecución

**1. Clonar el repositorio y entrar a la carpeta:**
```bash
git clone <url-del-repositorio>
cd practica_2
```

**2. Instalar Tkinter (solo Ubuntu/Debian):**
```bash
sudo apt-get install python3-tk
```

**3. Crear y activar el entorno virtual:**
```bash
python3 -m venv venv
source venv/bin/activate        # Linux / Mac
venv\Scripts\activate           # Windows
```

**4. Instalar dependencias:**
```bash
pip install -r requirements.txt
```

**5. Ejecutar los tests:**
```bash
python -m pytest tests/ -v
```

**6. Lanzar la aplicación:**
```bash
python main.py
```

> Para desactivar el entorno virtual cuando termines: `deactivate`

---

## Ejecución con Docker

**Correr los tests dentro de un contenedor:**
```bash
docker compose up tests
```

**Lanzar la interfaz gráfica con Docker (requiere servidor X11 en el host):**
```bash
xhost +local:docker
docker compose --profile gui up app
```

**Construir la imagen manualmente:**
```bash
docker build -t practica2 .
```

---

## Tests

El proyecto incluye **18 pruebas automatizadas** organizadas en dos archivos:

`tests/test_puzzle.py` cubre la verificación de solubilidad, la generación de vecinos, la admisibilidad de las tres heurísticas, la resolución correcta con cada heurística en estados de distinta dificultad, la validez del camino solución y la comparación de nodos expandidos entre heurísticas.

`tests/test_sudoku.py` cubre el conteo de conflictos, el relleno inicial de bloques, la resolución con A* en el nivel fácil, la preservación de celdas fijas tanto en A* como en SA, la reducción de conflictos de SA en los tres niveles y la presencia de métricas en los resultados.

Para ejecutar con reporte de cobertura:
```bash
python -m pytest tests/ -v --cov=src --cov-report=term-missing
```

---

## GitHub Actions

El flujo de CI definido en `.github/workflows/ci.yml` se activa automáticamente en cada `push` o `pull request` a las ramas `main` y `master`. Ejecuta los tests sobre Python 3.10 y 3.11 en paralelo, instala las dependencias del sistema y de Python, corre pytest con reporte de cobertura y sube el archivo `coverage.xml` como artefacto descargable desde la pestaña Actions del repositorio.