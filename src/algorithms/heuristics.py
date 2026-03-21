"""
Heurísticas para el algoritmo A* aplicadas al N-Puzzle.
 
Heurística 1 – Fichas fuera de lugar  : cuenta piezas no en su posición objetivo.
Heurística 2 – Distancia Manhattan    : suma de distancias fila+columna a meta.
Heurística 3 – Conflicto Lineal       : Manhattan + penalización por cruces (personalizada).
 
Las tres son ADMISIBLES (nunca sobreestiman el costo real).
"""
 
 
def misplaced_tiles(state: tuple, goal: tuple, size: int = None) -> int:
    """Cuenta fichas que no están en su posición objetivo (excluye el espacio vacío)."""
    return sum(1 for s, g in zip(state, goal) if s != 0 and s != g)
 
 
def manhattan_distance(state: tuple, goal: tuple, size: int) -> int:
    """
    Suma de distancias Manhattan de cada ficha a su posición objetivo.
    Más informativa que fichas fuera de lugar.
    """
    total = 0
    for val in range(1, size * size):
        if val in state:
            ci, gi = state.index(val), goal.index(val)
            cr, cc = divmod(ci, size)
            gr, gc = divmod(gi, size)
            total += abs(cr - gr) + abs(cc - gc)
    return total
 
 
def linear_conflict(state: tuple, goal: tuple, size: int) -> int:
    """
    Heurística personalizada: Manhattan + Conflicto Lineal.
 
    Dos fichas tj y tk están en conflicto lineal si:
      - Ambas están en la misma fila/columna que su celda objetivo.
      - Sus celdas objetivo están en la misma fila/columna.
      - El orden relativo entre ellas es invertido respecto al objetivo.
 
    Cada par en conflicto añade 2 movimientos extra (uno debe salir y volver).
    Garantiza ser >= Manhattan y sigue siendo admisible.
    """
    total = manhattan_distance(state, goal, size)
 
    # Conflictos en filas
    for row in range(size):
        tiles_in_row = []
        for col in range(size):
            val = state[row * size + col]
            if val != 0:
                g_row, g_col = divmod(goal.index(val), size)
                if g_row == row:
                    tiles_in_row.append((val, g_col))
        for i in range(len(tiles_in_row)):
            for j in range(i + 1, len(tiles_in_row)):
                if tiles_in_row[i][1] > tiles_in_row[j][1]:
                    total += 2
 
    # Conflictos en columnas
    for col in range(size):
        tiles_in_col = []
        for row in range(size):
            val = state[row * size + col]
            if val != 0:
                g_row, g_col = divmod(goal.index(val), size)
                if g_col == col:
                    tiles_in_col.append((val, g_row))
        for i in range(len(tiles_in_col)):
            for j in range(i + 1, len(tiles_in_col)):
                if tiles_in_col[i][1] > tiles_in_col[j][1]:
                    total += 2
 
    return total
 
 
HEURISTICS = {
    "Fichas fuera de lugar": misplaced_tiles,
    "Distancia Manhattan": manhattan_distance,
    "Conflicto Lineal": linear_conflict,
}
 