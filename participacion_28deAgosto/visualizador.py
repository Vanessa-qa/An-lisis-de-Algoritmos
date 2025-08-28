import tkinter as tk
import random
import time

# ---------------------------
# Parámetros generales
# ---------------------------
ANCHO = 800
ALTO = 300
N_BARRAS = 40
VAL_MIN, VAL_MAX = 5, 100
RETARDO_MS = 50  # velocidad en milisegundos

# ---------------------------
# Algoritmo: Selection Sort
# ---------------------------
def selection_sort_steps(data, draw_callback):
    """
    Selection Sort paso a paso.
    - data: lista (se modifica in-place)
    - draw_callback: función que redibuja el Canvas y puede resaltar índices
    """
    n = len(data)
    for i in range(n):
        min_idx = i
        for j in range(i + 1, n):
            draw_callback(activos=[i, j, min_idx])
            yield
            if data[j] < data[min_idx]:
                min_idx = j
        # Intercambio
        data[i], data[min_idx] = data[min_idx], data[i]
        draw_callback(activos=[i, min_idx])
        yield
    draw_callback(activos=[])

# ---------------------------
# Algoritmo: Merge Sort
# ---------------------------
def merge_sort_steps(data, draw_callback):
    def merge_sort(left, right):
        if right - left > 1:
            mid = (left + right) // 2
            yield from merge_sort(left, mid)
            yield from merge_sort(mid, right)

            merged = []
            i, j = left, mid

            while i < mid and j < right:
                draw_callback(activos=[i, j])
                yield
                if data[i] < data[j]:
                    merged.append(data[i])
                    i += 1
                else:
                    merged.append(data[j])
                    j += 1

            while i < mid:
                merged.append(data[i])
                i += 1
            while j < right:
                merged.append(data[j])
                j += 1

            for idx, val in enumerate(merged):
                data[left + idx] = val
                draw_callback(activos=[left + idx])
                yield

    yield from merge_sort(0, len(data))
    draw_callback(activos=[])

# ---------------------------
# Función de dibujo (énfasis)
# ---------------------------
def dibujar_barras(canvas, datos, activos=None):
    canvas.delete("all")
    if not datos:
        return
    n = len(datos)
    margen = 10
    ancho_disp = ANCHO - 2 * margen
    alto_disp = ALTO - 2 * margen
    w = ancho_disp / n
    esc = alto_disp / max(datos)

    for i, v in enumerate(datos):
        x0 = margen + i * w
        x1 = x0 + w * 0.9
        h = v * esc
        y0 = ALTO - margen - h
        y1 = ALTO - margen

        color = "#f1a0dd"
        if activos and i in activos:
            color = "#f3e850"
        canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

    canvas.create_text(6, 6, anchor="nw", text=f"n={len(datos)}", fill="#666")

# ---------------------------
# Aplicación principal
# ---------------------------
datos_selection = []
datos_merge = []
root = tk.Tk()
root.title("Visualizador de Metodos de Ordenamiento")

canvas_selection = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas_selection.pack(padx=10, pady=5)
canvas_merge = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas_merge.pack(padx=10, pady=5)

def generar():
    global datos_selection, datos_merge
    random.seed(time.time())
    lista = [random.randint(VAL_MIN, VAL_MAX) for _ in range(N_BARRAS)]
    datos_selection = lista.copy()
    datos_merge = lista.copy()
    dibujar_barras(canvas_selection, datos_selection)
    dibujar_barras(canvas_merge, datos_merge)

def ordenar_selection():
    if not datos_selection:
        return
    gen = selection_sort_steps(datos_selection, lambda activos=None: dibujar_barras(canvas_selection, datos_selection, activos))

    def paso():
        try:
            next(gen)
            root.after(RETARDO_MS, paso)
        except StopIteration:
            pass

    paso()

def ordenar_merge():
    if not datos_merge:
        return
    gen = merge_sort_steps(datos_merge, lambda activos=None: dibujar_barras(canvas_merge, datos_merge, activos))

    def paso():
        try:
            next(gen)
            root.after(RETARDO_MS, paso)
        except StopIteration:
            pass

    paso()

# ---------------------------
# Botones (UI mínima)
# ---------------------------
panel = tk.Frame(root)
panel.pack(pady=6)
tk.Button(panel, text="Generar", command=generar).pack(side="left", padx=5)
tk.Button(panel, text="Ordenar (Selection)", command=ordenar_selection).pack(side="left", padx=5)
tk.Button(panel, text="Ordenar (Merge)", command=ordenar_merge).pack(side="left", padx=5)

# ---------------------------
# Estado inicial
# ---------------------------
generar()       # crea y dibuja datos al abrir
root.mainloop() # inicia la app