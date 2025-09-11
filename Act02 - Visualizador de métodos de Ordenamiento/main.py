import tkinter as tk
from tkinter import ttk, messagebox
import random
import time

# Equipo:
# Gutierrez Vazquez Axel
# Quintero Arreola Laura Vanessa

# IMPORT PARA GRAFICAR
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MATPLOTLIB_OK = True
except Exception:
    MATPLOTLIB_OK = False

# ---------------------------
# Parametros generales
# ---------------------------
ANCHO = 800
ALTO = 300
VAL_MIN, VAL_MAX = 5, 100
RETARDO_MS = 50  # velocidad en milisegundos
N_BARRAS = 40    # valor por defecto para el entry

# ---------------------------
# Algoritmo: Selection Sort
# ---------------------------
def selection_sort_steps(data, draw_callback):
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
# Algoritmo: Bubble Sort
# ---------------------------
def bubble_sort_steps(data, draw_callback):
    n = len(data)
    for i in range(n):
        for j in range(0, n - i - 1):
            draw_callback(activos=[j, j + 1])
            yield
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
                draw_callback(activos=[j, j + 1])
                yield
    draw_callback(activos=[])

# ---------------------------
# Algoritmo: Quick Sort
# ---------------------------
def quick_sort_steps(data, draw_callback):
    def quick_sort(low, high):
        if low < high:
            pivot_index = yield from partition(low, high)
            yield from quick_sort(low, pivot_index - 1)
            yield from quick_sort(pivot_index + 1, high)

    def partition(low, high):
        pivot = data[high]
        i = low - 1
        for j in range(low, high):
            draw_callback(activos=[j, high])
            yield
            if data[j] < pivot:
                i += 1
                data[i], data[j] = data[j], data[i]
                draw_callback(activos=[i, j])
                yield
        data[i + 1], data[high] = data[high], data[i + 1]
        draw_callback(activos=[i + 1, high])
        yield
        return i + 1

    yield from quick_sort(0, len(data) - 1)
    draw_callback(activos=[])


# ---------------------------
# Funcion de dibujo (enfasis)
# ---------------------------
def dibujar_barras(canvas, datos, sort, activos=None):
    canvas.delete("all")
    # si no hay datos, dibujamos solo el titulo (n=0) y salimos
    if not datos:
        canvas.create_text(6, 6, anchor="nw", text=f"{sort} | n=0", fill="#666")
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

    canvas.create_text(6, 6, anchor="nw", text=f"{sort} | n={len(datos)}", fill="#666")


# ---------------------------
# Aplicacion principal
# ---------------------------
datos_selection = []
datos_merge = []
datos_bubble = [] #<--- Agrege la captura de bubble （〃｀ 3′〃）
datos_quick = [] #<--- Agrege la captura de quicksort 
root = tk.Tk()
root.title("Visualizador de Metodos de Ordenamiento")

canvas_selection = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas_selection.grid(row=0, column=0, padx=10, pady=5)
canvas_merge = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas_merge.grid(row=0, column=1, padx=10, pady=5)
canvas_bubble = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas_bubble.grid(row=1, column=0, padx=10, pady=5)
canvas_quick = tk.Canvas(root, width=ANCHO, height=ALTO, bg="white")
canvas_quick.grid(row=1, column=1, padx=10, pady=5)

# ---------------------------
# Tabla de tiempos (ahora: filas por N, Metodo, Tiempo)
# ---------------------------
# estructura: tiempos_by_n = { n1: { "Selection": t, "Merge": t2, ... }, n2: {...} }
tiempos_by_n = {}
ns_order = []  # lista con los valores de n en el orden en que el usuario genero

tabla_frame = tk.Frame(root)
tabla_frame.grid(row=3, column=0, columnspan=2, pady=(6,0))

columns = ("N", "Metodo", "Tiempo (s)")
tree = ttk.Treeview(tabla_frame, columns=columns, show="headings", height=6)
tree.heading("N", text="N")
tree.heading("Metodo", text="Metodo")
tree.heading("Tiempo (s)", text="Tiempo (s)")
tree.column("N", width=60, anchor="center")
tree.column("Metodo", width=150, anchor="center")
tree.column("Tiempo (s)", width=120, anchor="center")
tree.pack(side="left", padx=(10,0))

# scrollbar para la tabla si hace falta
scroll_tabla = ttk.Scrollbar(tabla_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scroll_tabla.set)
scroll_tabla.pack(side="left", fill="y")

def actualizar_tabla():
    """Redibuja la tabla a partir del dict 'tiempos_by_n' (mantener orden de N)."""
    # limpiar
    for item in tree.get_children():
        tree.delete(item)
    # insertar (en orden de ns_order)
    for n in ns_order:
        row = tiempos_by_n.get(n, {})
        # insertar una fila por cada metodo registrado para ese n
        for metodo in ["Selection", "Merge", "Bubble", "Quick"]:
            if metodo in row:
                tree.insert("", "end", values=(n, metodo, f"{row[metodo]:.6f}"))

# ---------------------------
# Funcion generar
# ---------------------------
# guardamos el N ultimo generado en last_generated_n para asociar mediciones al generar actual
last_generated_n = None

def generar():
    global datos_selection, datos_merge, datos_bubble, datos_quick, last_generated_n
    random.seed(time.time())
    lista = [random.randint(VAL_MIN, VAL_MAX) for _ in range(N_BARRAS)]
    datos_selection = lista.copy()
    datos_merge = lista.copy()
    datos_bubble = lista.copy()
    datos_quick = lista.copy()
    # guardamos el N actual
    last_generated_n = N_BARRAS
    # añadir a ns_order si es nuevo (mantiene orden de generaciones)
    if last_generated_n not in ns_order:
        ns_order.append(last_generated_n)
    dibujar_barras(canvas_selection, datos_selection, "Selection")
    dibujar_barras(canvas_merge, datos_merge, "Merge")
    dibujar_barras(canvas_bubble, datos_bubble, "Bubble")
    dibujar_barras(canvas_quick, datos_quick, "Quick")

# ---------------------------
# Funcion ordenar (usa dropdown) + medir tiempo (guarda en tiempos_by_n)
# ---------------------------
def ordenar():
    algoritmo = combo_algoritmo.get()

    # elegir generador y canvas/datos correspondiente
    if algoritmo == "Selection":
        gen = selection_sort_steps(datos_selection, lambda activos=None: dibujar_barras(canvas_selection, datos_selection, "Selection", activos))
    elif algoritmo == "Merge":
        gen = merge_sort_steps(datos_merge, lambda activos=None: dibujar_barras(canvas_merge, datos_merge, "Merge", activos))
    elif algoritmo == "Bubble":
        gen = bubble_sort_steps(datos_bubble, lambda activos=None: dibujar_barras(canvas_bubble, datos_bubble, "Bubble", activos))
    elif algoritmo == "Quick":
        gen = quick_sort_steps(datos_quick, lambda activos=None: dibujar_barras(canvas_quick, datos_quick, "Quick", activos))
    else:
        return

    # medimos tiempo real de ejecucion hasta completar el generador
    start = time.perf_counter()

    def paso():
        nonlocal start
        try:
            next(gen)
            root.after(scale_vel.get(), paso)
        except StopIteration:
            # calcular tiempo y guardar en tabla sin notificaciones
            elapsed = time.perf_counter() - start
            # asociar al ultimo N generado (si no hay, asociar al valor actual N_BARRAS)
            n_key = last_generated_n if last_generated_n is not None else N_BARRAS
            if n_key not in tiempos_by_n:
                tiempos_by_n[n_key] = {}
            tiempos_by_n[n_key][algoritmo] = elapsed
            # asegurarnos de tener el n en ns_order (si se midio sin generar explicito)
            if n_key not in ns_order:
                ns_order.append(n_key)
            actualizar_tabla()
            return

    paso()

# ---------------------------
# Botones de limpiar y mezclar
# ---------------------------
def limpiar():
    # redibuja cada canvas con lista vacia (pero sin borrar los datos de memoria)
    dibujar_barras(canvas_selection, [], "Selection")
    dibujar_barras(canvas_merge, [], "Merge")
    dibujar_barras(canvas_bubble, [], "Bubble")
    dibujar_barras(canvas_quick, [], "Quick")

def mezclar():
    global datos_bubble, datos_merge, datos_quick, datos_selection
    random.shuffle(datos_selection)
    random.shuffle(datos_merge)
    random.shuffle(datos_quick)
    random.shuffle(datos_bubble)

    dibujar_barras(canvas_selection, datos_selection, "Selection")
    dibujar_barras(canvas_merge, datos_merge, "Merge")
    dibujar_barras(canvas_bubble, datos_bubble, "Bubble")
    dibujar_barras(canvas_quick, datos_quick, "Quick")

# ---------------------------
# mostrar grafica y limpiar tabla
# ---------------------------
def mostrar_grafica():
    if not MATPLOTLIB_OK:
        messagebox.showerror("matplotlib requerido", "Instala matplotlib para mostrar la grafica (pip install matplotlib).")
        return

    # tomamos los Ns en el orden de ns_order
    if not ns_order:
        messagebox.showinfo("Sin datos", "No hay mediciones para graficar.")
        return

    orden_metodos = ["Selection", "Merge", "Bubble", "Quick"]
    xs = list(range(len(ns_order)))
    xticks = ns_order  # etiquetas N

    fig, ax = plt.subplots(figsize=(7,4))
    ax.set_xticks(xs)
    ax.set_xticklabels([str(n) for n in xticks])
    ax.set_xlabel("n (tamaño de la lista)")
    ax.set_ylabel("Tiempo (s)")
    ax.set_title("Tiempos de ejecucion por metodo y n")

    # para cada metodo, recoger y plotear sus puntos (si tiene)
    colores = {"Selection":"magenta", "Merge":"yellow", "Bubble":"purple", "Quick":"pink"}
    for metodo in orden_metodos:
        ys = []
        x_plot = []
        for i, n in enumerate(ns_order):
            row = tiempos_by_n.get(n, {})
            if metodo in row:
                x_plot.append(i)
                ys.append(row[metodo])
        if not ys:
            continue
        # puntos
        ax.scatter(x_plot, ys, label=metodo, color=colores.get(metodo))
        # unir si tiene 2 o mas puntos
        if len(x_plot) >= 2:
            ax.plot(x_plot, ys, color=colores.get(metodo))

    ax.legend()
    fig.tight_layout()

    # mostrar en ventana nueva
    win = tk.Toplevel(root)
    win.title("Grafica de tiempos")
    canvas_fig = FigureCanvasTkAgg(fig, master=win)
    canvas_fig.get_tk_widget().pack(fill="both", expand=True)
    canvas_fig.draw()

def limpiar_tabla():
    tiempos_by_n.clear()
    ns_order.clear()
    actualizar_tabla()

# ---------------------------
# Botones (UI minima) 
# ---------------------------
panel = tk.Frame(root)
panel.grid(row=2, column=0, columnspan=2, pady=6)

tk.Button(panel, text="Generar", command=generar).pack(side="left", padx=5)

# Entry para tamaño de lista
tk.Label(panel, text="N barras:").pack(side="left", padx=(10, 2))
entry_n = tk.Entry(panel, width=5)
entry_n.pack(side="left", padx=5)
entry_n.insert(0, str(N_BARRAS))  # valor inicial

# Boton aplicar tamaño (solo actualiza N_BARRAS, no genera)
def aplicar_n():
    global N_BARRAS
    try:
        val = int(entry_n.get())
        if val < 1:
            val = 1
    except ValueError:
        val = 40
    N_BARRAS = val
    entry_n.delete(0, "end")
    entry_n.insert(0, str(N_BARRAS))

tk.Button(panel, text="Aplicar", command=aplicar_n).pack(side="left", padx=5)

# Dropdown con algoritmos
tk.Label(panel, text="Algoritmo:").pack(side="left", padx=(10, 2))
combo_algoritmo = ttk.Combobox(panel, values=["Selection", "Merge", "Bubble", "Quick"], state="readonly", width=12)
combo_algoritmo.current(0)
combo_algoritmo.pack(side="left", padx=5)

tk.Button(panel, text="Ordenar", command=ordenar).pack(side="left", padx=5)
tk.Button(panel, text="Limpiar", command=limpiar).pack(side="left", padx=5)
tk.Button(panel, text="Mezclar", command=mezclar).pack(side="left", padx=5)

# Control de velocidad (Scale)
tk.Label(panel, text="Velocidad:").pack(side="left", padx=(10, 2))
scale_vel = tk.Scale(panel, from_=1, to=200, orient="horizontal")
scale_vel.set(RETARDO_MS)
scale_vel.pack(side="left", padx=5)

# Botones relacionados con la tabla
tk.Button(panel, text="Mostrar grafica", command=mostrar_grafica).pack(side="left", padx=5)
tk.Button(panel, text="Limpiar tabla", command=limpiar_tabla).pack(side="left", padx=5)

# ---------------------------
# Estado inicial
# ---------------------------
generar()       # crea y dibuja datos al abrir
actualizar_tabla()  # muestra la tabla vacia inicialmente
root.mainloop() # inicia la app