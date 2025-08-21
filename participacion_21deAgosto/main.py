import random
import time
import matplotlib.pyplot as plt

#Para generar una lista
def generate_list(size: int) -> list:
    lista = []
    for i in range(size):
        lista.append(random.randint(1, size))
    return lista

#Bubblesort
def bubblesort(vectorbs: list) -> None:
    # Iniciar temporizador
    inicio = time.time()
    
    n = len(vectorbs)
    for i in range(n - 1):
        for j in range(n - i - 1):
            if vectorbs[j] > vectorbs[j + 1]:
                vectorbs[j], vectorbs[j + 1] = vectorbs[j + 1], vectorbs[j]
    
    # Terminar temporizador
    fin = time.time()
    return (fin - inicio)*1000

#MergeSort
def mergesort(vectormerge: list) -> None:
    def merge(vectormerge):
        if len(vectormerge) > 1:
            medio = len(vectormerge) // 2

            izq = vectormerge[:medio]
            der = vectormerge[medio:]

            merge(izq)
            merge(der)

            i = j = k = 0

            while i < len(izq) and j < len(der):
                if izq[i] < der[j]:
                    vectormerge[k] = izq[i]
                    i += 1
                else:
                    vectormerge[k] = der[j]
                    j += 1
                k += 1

            while i < len(izq):
                vectormerge[k] = izq[i]
                i += 1
                k += 1

            while j < len(der):
                vectormerge[k] = der[j]
                j += 1
                k += 1

    inicio = time.time()
    merge(vectormerge)
    fin = time.time()
    return (fin - inicio)*1000

#QuickSort
def quicksort(vectorquick: list) -> None:
    def quick(arr, start, end):
        if start >= end:
            return

        def particion(arr, start, end):
            pivot = arr[start]
            menor = start + 1
            mayor = end

            while True:
                while menor <= mayor and arr[mayor] >= pivot:
                    mayor -= 1
                while menor <= mayor and arr[menor] <= pivot:
                    menor += 1
                if menor <= mayor:
                    arr[menor], arr[mayor] = arr[mayor], arr[menor]
                else:
                    break

            arr[start], arr[mayor] = arr[mayor], arr[start]
            return mayor

        p = particion(arr, start, end)
        quick(arr, start, p - 1)
        quick(arr, p + 1, end)

    inicio = time.time()
    quick(vectorquick, 0, len(vectorquick) - 1)
    fin = time.time()
    return (fin - inicio)*1000

# Lista de tamaños para probar
tamaños = [500, 1000, 2000, 4000]

tiempos_bubble = []
tiempos_merge = []
tiempos_quick = []

for size in tamaños:
    lista_original = generate_list(size)

    lista_bubble = lista_original.copy()
    lista_merge = lista_original.copy()
    lista_quick = lista_original.copy()

    print(f"Ordenando lista de tamaño {size}...")

    tiempo_b = bubblesort(lista_bubble)
    tiempo_m = mergesort(lista_merge)
    tiempo_q = quicksort(lista_quick)

    tiempos_bubble.append(tiempo_b)
    tiempos_merge.append(tiempo_m)
    tiempos_quick.append(tiempo_q)

# Graficar líneas para cada algoritmo
plt.plot(tamaños, tiempos_bubble, marker='o', color='red', label='Bubble Sort')
plt.plot(tamaños, tiempos_merge, marker='o', color='blue', label='Merge Sort')
plt.plot(tamaños, tiempos_quick, marker='o', color='green', label='Quick Sort')

plt.xlabel('Tamaño de la lista')
plt.ylabel('Tiempo (ms)')
plt.title('Comparación de tiempos de ordenamiento')
plt.legend()
plt.grid(True)
plt.show()