#Participacion de 18 de septiembre
#Problema del viajero
from itertools import permutations  # Importa permutaciones para generar todas las posibles rutas
import math
#Grafo con las rutas que puede recorrer el viajero
grafo_ponderado = {
    'a' : [('b', 2), ('c', 5), ('d', 7)],
    'b' : [('a', 2), ('c', 8), ('d', 3)],
    'c' : [('a', 5), ('b', 8), ('d', 1)],
    'd' : [('c', 1), ('a', 7), ('b', 3)]
}

#Calculos

nodos = sorted(grafo_ponderado.keys()) #ordena la lista 
cost = {u: {v: math.inf for v in nodos} for u in nodos}  #se crea una matriz de costos
for u, vecinos in grafo_ponderado.items(): #rellena la matriz de costos 
    for v, w in vecinos:
        cost[u][v] = w

# Funcion para calcular el costo de una ruta -- Naturalmente va a regresar a donde empezo en este caso a
def costo_ruta(ruta):
    total = 0
    for i in range(len(ruta) - 1): #suma los costos de cada tramo
        total += cost[ruta[i]][ruta[i + 1]]
    total += cost[ruta[-1]][ruta[0]]  #-- aQUI regresa a "a" y suma el costo
    return total

#Fuerza bruta para cada origen (a, b, c, d, ...)
for origen in nodos:
    otros = [n for n in nodos if n != origen]

    mejor_cost = math.inf
    mejores_rutas = []

    for perm in permutations(otros):  #recorre las permutaciones posibles dentro de los otros nodos
        ruta = [origen] + list(perm)   #Crea una ruta empezando en a 
        c = costo_ruta(ruta)            #calcula el costo de la ruta
        # si el costo es mejor que el actual se actualiza
        if c < mejor_cost:              
            mejor_cost = c
            mejores_rutas = [ruta.copy()]
        # si el costo es igual al actual, guarda tambien esa ruta 
        elif c == mejor_cost:
            mejores_rutas.append(ruta.copy())

    #Mostrar resultado para este origen
    print(f"----{origen}------")
    print(f"Mejor costo encontrado: {mejor_cost}")
    print("Mejores rutas:")
    for r in mejores_rutas:
        print(f"- {' -> '.join(r)} -> {origen}")
