import time
import sys
import matplotlib.pyplot as plt

# Fibonacci con programacion dinamica
def fibonacci_programacion_dinamica(n):
    if n <= 1:
        return n, list(range(n + 1))
    
    lista_fibonacci = [0, 1]
    for i in range(2, n + 1):
        lista_fibonacci.append(lista_fibonacci[i - 1] + lista_fibonacci[i - 2])
        
    return lista_fibonacci[n], lista_fibonacci

# Rango de valores de 'n' que vamos a probar
valores_n = range(1, 1001) 

# Listas para guardar los resultados de tiempo y espacio
tiempos_ejecucion = []
uso_memoria = []

# Medimos el tiempo y el espacio para cada valor de 'n'
for n_actual in valores_n:
    # Medir tiempo de ejecución
    tiempo_inicio = time.perf_counter()
    resultado, secuencia_fib = fibonacci_programacion_dinamica(n_actual)
    tiempo_final = time.perf_counter()
    
    # Guardamos el tiempo transcurrido
    tiempos_ejecucion.append(tiempo_final - tiempo_inicio)  
    # Medir el espacio utilizado por la lista que almacena la secuencia
    uso_memoria.append(sys.getsizeof(secuencia_fib))

plt.figure(figsize=(14, 6))

# Complejidad Temporal
plt.subplot(1, 2, 1)
plt.plot(valores_n, tiempos_ejecucion, label='Tiempo de ejecución real', color='pink')
plt.xlabel('Valor de n')
plt.ylabel('Tiempo (segundos)')
plt.title('Complejidad Temporal: O(n)')
plt.grid(True)
plt.legend()

# Complejidad Espacial
plt.subplot(1, 2, 2)
plt.plot(valores_n, uso_memoria, label='Uso de memoria real', color='purple')
plt.xlabel('Valor de n')
plt.ylabel('Espacio (bytes)')
plt.title('Complejidad Espacial: O(n)')
plt.grid(True)
plt.legend()

plt.tight_layout()
plt.show()