#Actividad Voraz Prim

print("Algoritmo Prim")
# Grafo no dirigido y ponderado
grafo = {
    'A':[('B', 1), ('D', 6)],
    'B':[('A', 1), ('D', 9), ('E', 8), ('F', 7), ('C',2)],
    'C':[('B', 2), ('F', 3)],
    'D':[('A', 6), ('B', 9), ('E', 5)],
    'E':[('D', 5), ('B', 8), ('F', 4)],
    'F':[('E', 4), ('B', 7), ('C', 3)]
}

# ------------- Algoritmo de Prim --------------
# Creamos el heap vacio para guardar los nodos
import heapq
heap = []
visitados = set()       # Nodos visitados
mst = []                # Arbol de Expansion Minima
total_prim = 0

# Sacamos las aritas de los nodos empezando por A
nodo_inicial = 'A'
visitados.add(nodo_inicial)

for vecino, peso in grafo[nodo_inicial]:
    heapq.heappush(heap, (peso, nodo_inicial, vecino))

# Continuamos sacando nodos por medio de la arista con menor peso
while heap:
    # Obtenemos la arista con menor peso
    peso, origen, destino = heapq.heappop(heap)

    # Si el nodo destino ya se visito continuamos
    if destino in visitados:
        continue

    # Si la arista es valida lo guardamos en mst
    mst.append((origen, destino, peso))
    total_prim += peso
    # Añadimos a nodos visitados
    visitados.add(destino)

    # Se agregan las nuevas aristas del nodo visitado
    for vecino, p in grafo[destino]:
        if vecino not in visitados:
            heapq.heappush(heap, (p, destino, vecino))

# Resultados del algoritmo de Prim
print("Arbol de Expansion Minima (MST):")
for origen, destino, peso in mst:
    print(f"{origen} -- {destino}  (peso {peso})")
print("Peso total:", total_prim)

#------------------------------------voraz de kruskal---------------------------------------

print("-------------------------------\nAlgoritmo Kruskal")

nodos = ["A", "B", "C", "D", "E", "F"]

aristas = [
    ('A', 'B', 1),
    ('A', 'D', 6),
    ('B', 'C', 2),
    ('B', 'D', 9),
    ('B', 'E', 8),
    ('B', 'F', 7),
    ('C', 'F', 3),
    ('D', 'E', 5),
    ('E', 'F', 4)
]

class UnionFind:
    def __init__(self, elementos):
        self.parent = {x: x for x in elementos}
        self.rank = {x: 0 for x in elementos}

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  #compresion
        return self.parent[x]

    def union(self, x, y):
        rx = self.find(x)
        ry = self.find(y)

        if rx == ry:
            return False  #ya estan conectados

        #unir por rank
        if self.rank[rx] < self.rank[ry]:
            self.parent[rx] = ry
        elif self.rank[rx] > self.rank[ry]:
            self.parent[ry] = rx
        else:
            self.parent[ry] = rx
            self.rank[rx] += 1

        return True
    
aristas_ordenadas = sorted(aristas, key=lambda x: x[2])    

uf = UnionFind(nodos)

mst = []      #lista donde se guardan las aristas
total = 0   #acumulador

for u, v, peso in aristas_ordenadas:
    if uf.union(u, v):             # si no forma ciclo
        mst.append((u, v, peso))   # la agrega al MST
        total += peso

print("Aristas seleccionadas en el MST:")
for u, v, peso in mst:
    print(u, "-", v, "peso:", peso)

print("Peso total:", total)