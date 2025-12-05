# Problema del Viajero (Travelling Salesman Problem)

# Usamos la siguiente libreria para las permutaciones
from itertools import permutations

# Primero guardamos los nombres de la ciudades
ciudades = ["Guadalajara", "Monterrey",
            "Merida", "Morelia", "Veracruz",
            "Tijuana", "Durango", "Chihuahua"]

# Después definimos las distancias en una matriz
distancias = [
    [0,   680,  1900, 290,  780,  2350, 430,  920],   # Guadalajara
    [680,   0,  1800, 830,  900,  2300, 560,  240],   # Monterrey
    [1900, 1800,   0, 1670, 990,  3500, 1640, 2200],  # Mérida
    [290,  830, 1670,   0,  600,  2600, 500, 1100],   # Morelia
    [780,  900,  990,  600,   0,  2950, 930, 1450],   # Veracruz
    [2350, 2300, 3500, 2600, 2950,   0, 1700, 1350],  # Tijuana
    [430,  560, 1640, 500,  930,  1700,   0,  620],   # Durango
    [920,  240, 2200, 1100, 1450, 1350, 620,   0]     # Chihuahua
]

# Guadalajara sera la ciudad de origen
inicio = 0

# Ahora usamos la libreria para todas las posibles rutas
rutas = permutations(range(1, len(ciudades)))

# Despues guardamos la mejor ruta encontrada
mejor_ruta = None
mejor_distancia = float("inf")

# Funcion para calcular la distancia total
def calcular_distancia(ruta, distancias):
    # Inicializamos la variable en cero
    distancia_total = 0

    # Recorremos la ruta desde el primer punto hasta el penultimo
    for i in range(len(ruta) - 1):
        # Sumamos la distancia entre la ciudad actual y la que sigue
        distancia_total += distancias[ruta[i]][ruta[i+1]]

    return distancia_total

# Ahora probamos todas las rutas posibles
for r in rutas:
    # Creamos la ruta iniciando y terminando en Guadalajara
    ruta_completa = [inicio] + list(r) + [inicio]

    # Calculamos la distancia total de esta ruta
    distancia = calcular_distancia(ruta_completa, distancias)

    # Revisamos si es mejor que la mejor ruta encontrada
    if distancia < mejor_distancia:
        mejor_distancia = distancia
        mejor_ruta = ruta_completa

# Convertimos indices a nombres reales
ruta_nombres = [ciudades[c] for c in mejor_ruta]

print("Mejor ruta encontrada:")
print(" -> ".join(ruta_nombres))

print("Distancia total:", mejor_distancia, "km")