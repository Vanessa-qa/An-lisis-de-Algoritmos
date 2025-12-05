# fibonacci fuerzaBruta con entrada de usuario

import time
import tracemalloc
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os

def fib_fuerza_bruta(n: int) -> int:
    """Fuerza bruta"""
    if n <= 1:
        return n
    return fib_fuerza_bruta(n-1) + fib_fuerza_bruta(n-2)

def medir(n_values):
    tiempos = []
    memoria_kb = []
    resultados = []
    for n in n_values:
        tracemalloc.start()
        t0 = time.perf_counter()
        res = fib_fuerza_bruta(n)
        t1 = time.perf_counter()
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tiempos.append(t1 - t0)
        memoria_kb.append(peak / 1024.0)
        resultados.append(res)
        print(f"n={n}: fib={res}, Temporal={t1-t0:.6f}s, Espacial={peak/1024.0:.2f} KB")
    return tiempos, memoria_kb, resultados

def crear_figura_tiempo(n_values, tiempos):
    fig = Figure(figsize=(5,4))
    ax = fig.add_subplot(111)
    ax.plot(n_values, tiempos, marker='o')
    ax.set_xlabel("n")
    ax.set_ylabel("Tiempo (s)")
    ax.set_title("Complejidad temporal")
    ax.set_yscale('log')
    ax.grid(True)
    return fig

def crear_figura_memoria(n_values, memoria_kb):
    fig = Figure(figsize=(5,4))
    ax = fig.add_subplot(111)
    ax.plot(n_values, memoria_kb, marker='o')
    ax.set_xlabel("n")
    ax.set_ylabel("Memoria pico (KB)")
    ax.set_title("Complejidad espacial")
    ax.set_yscale('log')
    ax.grid(True)
    return fig

def mostrar_gui(fig_time, fig_mem):
    root = tk.Tk()
    root.title("Fibonacci - Fuerza Bruta: Temporal y Espacial")

    frame_left = tk.Frame(root)
    frame_left.pack(side="left", fill="both", expand=True, padx=8, pady=8)

    canvas_time = FigureCanvasTkAgg(fig_time, master=frame_left)
    canvas_time.draw()
    canvas_time.get_tk_widget().pack(fill="both", expand=True)

    frame_right = tk.Frame(root)
    frame_right.pack(side="right", fill="both", expand=True, padx=8, pady=8)

    canvas_mem = FigureCanvasTkAgg(fig_mem, master=frame_right)
    canvas_mem.draw()
    canvas_mem.get_tk_widget().pack(fill="both", expand=True)

    root.mainloop()

def main():
    try:
        n_user = int(input("Teclea un numero para comenzar\n->:"))
        if n_user < 0:
            print("el numero debe ser positivo")
            return
    except ValueError:
        print("el numero debe ser entero")
        return

    n_values = list(range(1, n_user + 1))

    print("\nMidiendo Fibonacci\n")
    tiempos, memoria_kb, resultados = medir(n_values)

    print(f"\nEl termino Fibonacci({n_user}) = {resultados[-1]}")

    fig_time = crear_figura_tiempo(n_values, tiempos)
    fig_mem = crear_figura_memoria(n_values, memoria_kb)

    try:
        mostrar_gui(fig_time, fig_mem)
    except Exception as e:
        folder = os.path.abspath(os.path.join(os.getcwd(), "fibonacci_output"))
        print("\nNo se pudo abrir la GUI (posible entorno sin DISPLAY).")
        print("Excepcion:", e)

if __name__ == "__main__":
    main()
