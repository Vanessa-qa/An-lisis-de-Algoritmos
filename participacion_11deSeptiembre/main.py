import math
import tkinter as tk
import random
import threading
from tkinter import scrolledtext

puntos = []  #lista vacia para almacenar los puntos

punto1 = None
punto2 = None
punto3 = None
punto4 = None
punto5 = None

#calcula la distancia euclidiana usando pow
def distancia(punto_uno, punto_dos):
    x1, y1 = punto_uno
    x2, y2 = punto_dos
    dx = x2 - x1
    dy = y2 - y1
    d = math.sqrt(pow(dx, 2) + pow(dy, 2))
    return d  

#constantes y listas para la GUI
numPuntos = 5
x = []
y = []
dist = []

# captura los valores ingresados en la GUI
def captura(count=numPuntos):
    puntos.clear()
    dist.clear()
    for i in range(count):
        x_val = float(x[i].get())
        y_val = float(y[i].get())
        puntos.append((x_val, y_val))
    actualizar()

#actualiza las variables globales con los puntos ingresados
def actualizar():
    global punto1, punto2, punto3, punto4, punto5
    puntos_pad = puntos + [None] * max(0, numPuntos - len(puntos))
    punto1, punto2, punto3, punto4, punto5 = puntos_pad[:numPuntos]

#calcula y muestra las distancias entre todos los pares de puntos
def calcular():
    resultados.delete("1.0", tk.END)
    captura()
    for i in range(len(puntos)):
        for j in range(i + 1, len(puntos)):
            pi = puntos[i]
            pj = puntos[j]
            d = distancia(pi, pj)
            dist.append(d)
            #linea amigable indicando cuales puntos se compararon
            friendly = f"Distancia P{i+1}-P{j+1} = {d:.2f}"
            resultados.insert(tk.END, friendly + "\n")
            print(friendly)
    if dist:
        min_dist = f"Distancia minima: {min(dist):.2f}"
        max_dist = f"Distancia maxima: {max(dist):.2f}"
        resultados.insert(tk.END, "\n" + min_dist + "\n" + max_dist + "\n")
        print("\n" + min_dist)
        print(max_dist)

#llena los puntos con valores aleatorios
def llenar(count=numPuntos):
    puntos.clear()
    dist.clear()
    for i in range(count):
        x_val = random.randint(0, 40)
        y_val = random.randint(0, 40)
        puntos.append((x_val, y_val))
        x[i].delete(0, tk.END)
        x[i].insert(0, str(x_val))
        y[i].delete(0, tk.END)
        y[i].insert(0, str(y_val))
    actualizar()
    resultados.insert(tk.END, "\nValores:\n")
    print("\nValores:")
    for idx, (x_val, y_val) in enumerate(puntos, 1):
        line = f"P{idx} = ({x_val}, {y_val})"
        resultados.insert(tk.END, line + "\n")
        print(line)

#limpia puntos y resultados
def limpiar():
    puntos.clear()
    dist.clear()
    actualizar()
    for e in x + y:
        e.delete(0, tk.END)
    resultados.delete("1.0", tk.END)
    print("\nPuntos y resultados eliminados")

#menu en terminal
def terminal():
    while True:
        print("\nOpciones:")
        print("(1) Llenar")
        print("(2) Ingresar puntos")
        print("(3) Calcular")
        print("(4) Limpiar")
        print("(0) Salir")
        opcion = input("->:  ").strip()
        if opcion == "1":
            llenar()
        elif opcion == "2":
            puntos.clear()
            for i in range(numPuntos):
                x_val = float(input(f"Ingrese X{i+1}: "))
                y_val = float(input(f"Ingrese Y{i+1}: "))
                puntos.append((x_val, y_val))
            actualizar()
            for i, (x_val, y_val) in enumerate(puntos):
                x[i].delete(0, tk.END)
                x[i].insert(0, str(x_val))
                y[i].delete(0, tk.END)
                y[i].insert(0, str(y_val))
        elif opcion == "3":
            calcular()
        elif opcion == "4":
            limpiar()
        elif opcion == "0":
            print("saliendo...")
            break

#construccion de la GUI
root = tk.Tk()
root.title("Comparador de Distancias")

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

tk.Label(frame, text="Punto").grid(row=0, column=0, padx=5, pady=5)
tk.Label(frame, text="X").grid(row=0, column=1, padx=5, pady=5)
tk.Label(frame, text="Y").grid(row=0, column=2, padx=5, pady=5)

for i in range(numPuntos):
    tk.Label(frame, text=f"P{i+1}").grid(row=i+1, column=0, padx=5, pady=3, sticky="w")
    ex = tk.Entry(frame, width=10)
    ey = tk.Entry(frame, width=10)
    ex.grid(row=i+1, column=1, padx=5, pady=3)
    ey.grid(row=i+1, column=2, padx=5, pady=3)
    x.append(ex)
    y.append(ey)

btn_frame = tk.Frame(frame)
btn_frame.grid(row=1, column=3, rowspan=5, padx=10)

btn_fill = tk.Button(btn_frame, text="Llenar", width=12, command=lambda: llenar(numPuntos))
btn_calc = tk.Button(btn_frame, text="Calcular", width=12, command=calcular)
btn_clear = tk.Button(btn_frame, text="Limpiar", width=12, command=limpiar)

btn_fill.pack(pady=5)
btn_calc.pack(pady=5)
btn_clear.pack(pady=5)

resultados = scrolledtext.ScrolledText(root, width=60, height=12)
resultados.pack(padx=10, pady=(5,10))

#iniciar el hilo de consola
threading.Thread(target=terminal, daemon=True).start()

actualizar()

root.mainloop()
