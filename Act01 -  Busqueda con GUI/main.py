import time as tm
import random
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

############################## algortimos ###########################################
#Para generar una lista
def generate_list(size: int) -> list:
    lista = []
    for i in range(size):
        lista.append(random.randint(1, size))
    lista.sort()
    return lista

#Con esta funcion capturamos el valor del tamaño de la lista 
def confirm_size():
    try:
        n = int(dropdown_menu.get()) #Seleccionamos el valor ingreado
        result_label.config(text=f"Lista de tamaño: {n}") 
        lista = generate_list(n) #Generamos la lista
        result_label.size = n #Guardamos el numero de elementos
        result_label.lista = lista #Guardamos la lista generada 
    except ValueError:
        result_label.config(text="Por favor escribe un número válido.")

def linear_search(lista, x): 
    for i in range(len(lista)): #Recorremos buscando el numero
        if lista[i] == x: #Comparamos los numeros
            return i #Retornamos el indice
    return "No encontrado" #En caso de no encontrar el numero

def binary_search(lista, x):
    #Definimos lado izquierdo y derecho
    left = 0
    right = len(lista) - 1

    while left <= right:
        half = (left + right) // 2
        if lista[half] == x:
            return half
        elif x < lista[half]:
            right = half - 1
        else:
            left = half + 1
    return "No encontrado"

# Diccionarios para guardar tiempos agrupados por tamaño
linear_times = {100: [], 1000: [], 10000: [], 100000: []}
binary_times = {100: [], 1000: [], 10000: [], 100000: []}

def search_result(type):
    lista = result_label.lista
    valor = int(entry_number.get())
    size = result_label.size
    if type == "lineal":
        start = tm.perf_counter()
        resultado = linear_search(lista, valor)
        end = tm.perf_counter()
        time = (end-start)*1000
        linear_times[size].append(time)
        search_result_label.config(text=f"{resultado}")
        time_result_label.config(text=f"{time}")
    else:
        start = tm.perf_counter()
        resultado = binary_search(lista, valor)
        end = tm.perf_counter()
        time = (end-start)*1000
        binary_times[size].append(time)
        search_result_label.config(text=f"{resultado}")
        time_result_label.config(text=f"{time}")
        

#Para generar una ventana que sera nuestra GUI y define el nombre y el tamaño
root = tk.Tk()
root.title("Búsqueda de Número Aleatorio")
root.geometry("700x700")

#Pregunta al usuario el tamaño de la lista
lbl = tk.Label(root, text="Escribe de cuántos números quieres la lista:")
lbl.pack(pady=10) #Espacio

############################## Frame para lista de opciones y boton ############################################
#Se utiliza frame para que cuando se solicite el tamaño el botón este a un lado
frame = tk.Frame(root)

#Para crear un dropdown menu declaramos las opciones Nota:usamos Combobox por que es mas estetico
options = [100, 1000, 10000, 100000]
#Creamos el dropdown menu
dropdown_menu = ttk.Combobox(frame,values=options)
#con grid ponemos en la posicion que queremos el elemento dentro del frame
dropdown_menu.grid(row=0, column=0)
dropdown_menu.set(options[0])

#Creamos el boton que genere la lista con la opcion de tamaño elegida
btn = tk.Button(frame, text="Generar lista", command=confirm_size)
btn.grid(row=0, column=1)

frame.pack(pady=5)
#################################################################################################################

# Mostramos al usuario que se genero su lista usando este label
result_label = tk.Label(root, text="")
result_label.pack(pady=10)

##################################### Frame para indicar numero a buscar y seleccionar tipo de busqueda ##########
search_frame = tk.Frame(root)

entry_label = tk.Label(search_frame, text="Ingresa el numero a buscar:")
entry_label.grid(row=0,column=0,padx=5, pady=5)

entry_number = tk.Entry(search_frame)
entry_number.grid(row=0, column=1,padx=5, pady=5)

lin_search_button = tk.Button(search_frame, text="Busqueda lineal", command=lambda: search_result("lineal"))
lin_search_button.grid(row=0, column=2, padx=5, pady=5)

bin_search_button = tk.Button(search_frame, text="Busqueda binaria", command=lambda: search_result("binaria"))
bin_search_button.grid(row=0, column=3, padx=5, pady=5)

search_frame.pack()
# Label para mostrar resultados de la búsqueda
results_label = tk.Label(root,text="Resultados de la busqueda:")
results_label.pack(anchor="w", padx=10, pady=10)

################## Frame para indicar los resultados de la busqueda ##################################
results_frame = tk.Frame(root)

index_label = tk.Label(results_frame, text="Indice del elemento buscado:")
index_label.grid(row=0, column=0, sticky="w")

search_result_label = tk.Label(results_frame, text="") 
search_result_label.grid(row=0, column=1, sticky="w")

time_label = tk.Label(results_frame, text="Tiempo de ejecución:")
time_label.grid(row=1, column=0)

time_result_label = tk.Label(results_frame, text="")
time_result_label.grid(row=1, column=1)

results_frame.pack()

###################### Frame para insertar la grafica de matplotlib ####################################

fig = Figure(figsize=(6, 4), dpi=100)
ax = fig.add_subplot(111)
ax.set_title("Promedio de tiempos por tamaño")
ax.set_ylabel("Tiempo de ejecución (ms)")
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH)

def update_graphic():
    ax.clear()
    ax.set_title("Promedio de tiempos por tamaño")
    ax.set_ylabel("Tiempo de ejecución (ms)")
    
    sizes = [100, 1000, 10000, 100000]
    x = np.arange(len(sizes))
    width = 0.35
    
    # Promedios
    lineal_means = [sum(linear_times[s])/len(linear_times[s]) if linear_times[s] else 0 for s in sizes]
    binaria_means = [sum(binary_times[s])/len(binary_times[s]) if binary_times[s] else 0 for s in sizes]
    
    ax.bar(x - width/2, lineal_means, width, label="Lineal", color="blue")
    ax.bar(x + width/2, binaria_means, width, label="Binaria", color="orange")
    
    ax.set_xticks(x)
    ax.set_xticklabels([str(s) for s in sizes])
    ax.set_xlabel("Tamaño de lista")
    ax.legend()
    
    canvas.draw()

btn_update = tk.Button(root, text="Actualizar gráfica", command=update_graphic)
btn_update.pack(pady=5)

root.mainloop()