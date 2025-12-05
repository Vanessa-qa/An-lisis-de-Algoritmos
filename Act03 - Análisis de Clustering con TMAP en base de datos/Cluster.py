#Quintero Arreola Laura Vanessa
#Gutierrez Vazquez Axel

#para ejecutar el codigo se deben ejecutar los isguientes comandos en el comand prompt de anaconda
#conda activate tmap-env
#cd C:\Users\axelg\Downloads\test
#python Cluster.py

#El codigo se ejecuta y posteriormente se abre en el navegador en el siguiente link (http://127.0.0.1:8050 en tu navegador)
#se usa ctrl + C para dejar de ejecutar

import os                                               # manejo de rutas y archivos del sistema operativo
import numpy as np                                      # libreria para operaciones numericas, especialmente con arrays
import pandas as pd                                     # libreria para manipulacion y analisis de datos, como leer CSVs
from sklearn.preprocessing import StandardScaler        # para normalizar los datos 
from umap import UMAP                                   # algoritmo para reduccion de dimensionalidad y visualizacion
from sklearn.cluster import KMeans                      # algoritmo para agrupar datos en clusters
from sklearn.neighbors import NearestNeighbors          # para encontrar los vecinos mas cercanos de un punto
from PIL import Image                                   # libreria para manipular imagenes
import io                                               # para manejar datos en memoria como si fueran archivos
import base64                                           # para codificar imagenes en texto y mostrarlas en la web
from scipy.spatial.distance import pdist, squareform    # para calcular matrices de distancia entre puntos
from scipy.sparse.csgraph import minimum_spanning_tree  # para calcular el arbol de conexion minima

import plotly.graph_objects as go                       # para crear figuras y graficos complejos en Plotly
import plotly.express as px                             # para funciones de alto nivel en Plotly, como paletas de colores

import dash                                             # framework principal para crear la aplicacion web
from dash import dcc, html                              # componentes de Dash para graficos y elementos HTML 
from dash.dependencies import Input, Output             # para definir la interactividad de la aplicacion (callbacks)

# -- PARAMETROS -----------------
CSV_PATH = "fashion-mnist_train.csv"                    # ruta al archivo de datos
SAMPLE_SIZE = 15000                                     # numero de filas a tomar del archivo CSV
DRESS_LABEL = 3                                         # el numero que representa a los vestidos en el dataset
N_SUBCLUSTERS = 7                                       # numero de grupos o clusters a crear

def cargar_subset(csv_path, n=None):
    """Lee el CSV y devuelve df completo, X (features) e y (labels); permite tomar un subset aleatorio."""
    df = pd.read_csv(csv_path)                            # lee el archivo CSV y lo carga en un DataFrame de pandas
    if n is not None and n < len(df):                     # si se especifico un tamano de muestra y es valido
        df = df.sample(n=n, random_state=42).reset_index(drop=True)  # toma una muestra aleatoria y reinicia los indices
    X = df.drop(columns=['label']).copy()                 # X contiene todas las columnas excepto 'label' (los pixeles)
    y = df['label'].copy()                                # y contiene solo la columna 'label' (las etiquetas)
    return df, X, y                                       # devuelve el DataFrame, los datos X y las etiquetas y

def imagen_base64_from_row(row):
    """Convierte una fila (784 valores de 28x28) a data URI PNG base64 para mostrar en <img>."""
    arr = np.array(row).reshape(28,28)                    # convierte la fila de datos en un array de 28x28
    if arr.max() <= 1.0:                                  # si el valor maximo de pixel es 1 o menos
        arr = (arr * 255).astype(np.uint8)                # escala los valores a 0-255
    else:
        arr = arr.astype(np.uint8)                        # si no, solo asegura que el tipo de dato sea correcto
    img = Image.fromarray(arr, mode='L')                  # crea un objeto de imagen en escala de grises desde el array
    buf = io.BytesIO()                                    # crea un buffer en memoria para guardar la imagen temporalmente
    img.save(buf, format='PNG')                           # guarda la imagen en formato PNG en el buffer
    b64 = base64.b64encode(buf.getvalue()).decode('ascii')# codifica la imagen del buffer a texto base64
    return f"data:image/png;base64,{b64}"                 # devuelve el string formateado para usar en una etiqueta <img> de HTML

if not os.path.exists(CSV_PATH):                          # comprueba si el archivo CSV existe en la ruta especificada
    raise FileNotFoundError(f"No se encontro {CSV_PATH}") # si no existe, detiene el programa y muestra un error

df, X, y = cargar_subset(CSV_PATH, n=SAMPLE_SIZE)         # llama a la funcion para cargar los datos
print(f"Cargado subset: {len(df)} filas.")                # imprime cuantas filas se cargaron

dress_idx = df[df['label'] == DRESS_LABEL].index          # encuentra los indices de todas las filas que son vestidos
X_dress = X.loc[dress_idx].reset_index(drop=True)         # crea un nuevo DataFrame solo con los datos de los vestidos
print(f"Vestidos en subset: {len(X_dress)}")              # imprime cuantos vestidos se encontraron

print("Generando imagenes base64...")
hover_imgs = [imagen_base64_from_row(X_dress.iloc[i].values) for i in range(len(X_dress))] # crea una lista de imagenes en base64 para cada vestido
print("Imagenes generadas.")

scaler = StandardScaler()                                 # crea una instancia del normalizador
X_scaled = scaler.fit_transform(X_dress)                  # normaliza los datos de los vestidos

print("Calculando disposicion con UMAP (esto puede tardar un poco)...")
reducer = UMAP(                                           # configura el algoritmo UMAP con parametros especificos
    n_neighbors=125,                                      # numero de vecinos a considerar para la estructura
    min_dist=0.0,                                         # distancia minima entre puntos
    spread=1.0,                                           # la dispersion de los puntos en la visualizacion
    repulsion_strength=0.1,                               # fuerza con que se repelen los clusters
    random_state=42                                       # semilla para que el resultado sea reproducible
)
coords_raw = reducer.fit_transform(X_scaled)              # aplica UMAP a los datos escalados para obtener coordenadas

print("Proyectando la disposicion en un circulo...")
center = coords_raw.mean(axis=0)                          # calcula el centro de la nube de puntos generada por UMAP
coords_centered = coords_raw - center                     # centra la nube de puntos en el origen (0,0)
radii = np.linalg.norm(coords_centered, axis=1)           # calcula la distancia de cada punto al centro
angles = np.arctan2(coords_centered[:, 1], coords_centered[:, 0]) # calcula el angulo de cada punto
radii_normalized = np.sqrt(radii / radii.max())           # normaliza los radios y aplica una transformacion para llenar el centro
coords = np.zeros_like(coords_raw)                        # crea un array vacio para las nuevas coordenadas
coords[:, 0] = radii_normalized * np.cos(angles)          # calcula la nueva coordenada X
coords[:, 1] = radii_normalized * np.sin(angles)          # calcula la nueva coordenada Y
coords *= 15                                              # escala el tamano total del grafico para mejor visualizacion

kmeans = KMeans(n_clusters=N_SUBCLUSTERS, random_state=42, n_init=10) # configura el algoritmo KMeans
subtypes = kmeans.fit_predict(coords)                     # agrupa las coordenadas en N_SUBCLUSTERS clusters

subtype_names = [                                         # define los nombres para cada cluster
    "Vestido Con Mangas",
    "Vestido Sin Mangas",
    "Vestido Con Mangas Largas",
    "Vestido Corto y Ajustado",
    "Vestido con Cuello Redondo",
    "Vestido de Noche Largo",
    "Vestido Camisero"
]

palette = px.colors.qualitative.Plotly                    # selecciona una paleta de colores
color_map = {i: palette[i % len(palette)] for i in range(N_SUBCLUSTERS)} # asigna un color a cada numero de cluster

print("Construyendo el arbol de conexion hibrido...")
dist_matrix = squareform(pdist(coords, 'euclidean'))      # calcula una matriz con la distancia entre cada par de puntos
mst = minimum_spanning_tree(dist_matrix).toarray()        # calcula el arbol de conexion minima a partir de la matriz de distancias

nbrs_model_radial = NearestNeighbors(n_neighbors=16).fit(coords) # prepara un modelo para encontrar los 16 vecinos mas cercanos
nodos_centrales = []                                      # lista para guardar los indices de los nodos centrales
nodos_radiales = set()                                    # conjunto para guardar los indices de los nodos externos
mapa_central_radial = {}                                  # diccionario para mapear cada nodo central a sus nodos externos

for i in range(N_SUBCLUSTERS):                            # itera sobre cada cluster
    mascara_cluster = (subtypes == i)                     # crea una mascara para seleccionar los puntos de este cluster
    indices_globales_cluster = np.where(mascara_cluster)[0] # obtiene los indices globales de esos puntos
    
    if len(indices_globales_cluster) > 0:                 # si el cluster no esta vacio
        coordenadas_cluster = coords[mascara_cluster]     # obtiene las coordenadas de los puntos del cluster
        centroide = coordenadas_cluster.mean(axis=0)      # calcula el centro geometrico (centroide) del cluster
        
        distancias_a_centroide = np.linalg.norm(coordenadas_cluster - centroide, axis=1) # calcula la distancia de cada punto del cluster a su centroide
        indice_nodo_central_en_cluster = np.argmin(distancias_a_centroide) # encuentra el indice (dentro del cluster) del punto mas cercano al centroide
        indice_global_nodo_central = indices_globales_cluster[indice_nodo_central_en_cluster] # convierte ese indice a un indice global
        nodos_centrales.append(indice_global_nodo_central) # anade este punto a la lista de nodos centrales
        
        distancias, indices = nbrs_model_radial.kneighbors([coords[indice_global_nodo_central]]) # encuentra los 16 vecinos del nodo central
        nodos_radiales_actuales = set()                   # crea un conjunto para los nodos externos de este nodo central
        for indice_radial in indices[0]:                  # itera sobre los vecinos
            if indice_radial != indice_global_nodo_central: # si el vecino no es el mismo nodo central
                nodos_radiales.add(indice_radial)         # anade el punto al conjunto de todos los nodos externos
                nodos_radiales_actuales.add(indice_radial)# anade el punto al conjunto de nodos externos de este nodo central
        mapa_central_radial[indice_global_nodo_central] = nodos_radiales_actuales # guarda la relacion nodo central -> nodos externos

edge_x = []                                               # lista para las coordenadas X de las lineas
edge_y = []                                               # lista para las coordenadas Y de las lineas

rows, cols = np.where(mst > 0)                            # encuentra las conexiones del arbol de conexion minima
for i, j in zip(rows, cols):                              # itera sobre cada conexion
    if i in nodos_radiales or j in nodos_radiales:        # si alguno de los puntos de la conexion es un nodo externo
        continue                                          # ignora esa conexion (la "corta")
    edge_x += [coords[i, 0], coords[j, 0], None]          # si no, anade la linea a la lista
    edge_y += [coords[i, 1], coords[j, 1], None]

for indice_nodo_central, nodos_radiales_actuales in mapa_central_radial.items(): # itera sobre cada nodo central y su grupo de nodos externos
    for indice_radial in nodos_radiales_actuales:         # itera sobre cada nodo externo
        edge_x += [coords[indice_nodo_central, 0], coords[indice_radial, 0], None] # anade la conexion nodo central -> nodo externo
        edge_y += [coords[indice_nodo_central, 1], coords[indice_radial, 1], None]

puntos_sistema_radial = nodos_radiales.union(set(nodos_centrales)) # crea un conjunto con todos los puntos que son nodos centrales o externos
indices_puntos_no_radiales = [i for i in range(len(coords)) if i not in puntos_sistema_radial] # crea una lista de puntos que no estan en ningun sistema de nodos

if indices_puntos_no_radiales:                            # si hay puntos fuera de los sistemas de nodos
    nbrs_puente = NearestNeighbors(n_neighbors=1).fit(coords[indices_puntos_no_radiales]) # prepara un modelo para buscar vecinos solo en esos puntos
    for indice_nodo_central in nodos_centrales:           # itera sobre cada nodo central
        distancias, indices = nbrs_puente.kneighbors([coords[indice_nodo_central]]) # encuentra el punto mas cercano al nodo central que no es parte de un sistema de nodos
        indice_final_puente = indices_puntos_no_radiales[indices[0][0]] # obtiene el indice global de ese punto
        edge_x += [coords[indice_nodo_central, 0], coords[indice_final_puente, 0], None] # anade la conexion "puente"
        edge_y += [coords[indice_nodo_central, 1], coords[indice_final_puente, 1], None]

centroids = np.array([coords[subtypes == i].mean(axis=0) for i in range(N_SUBCLUSTERS)])
central_sun_idx = np.argmin(np.linalg.norm(coords, axis=1))
for centroid in centroids:
    edge_x += [coords[central_sun_idx, 0], centroid[0], None]
    edge_y += [coords[central_sun_idx, 1], centroid[1], None]


edge_trace = go.Scatter(                                  # crea el objeto de trazado para todas las lineas
    x=edge_x, y=edge_y,                                   # asigna las coordenadas de las lineas
    line=dict(width=0.6, color='rgba(200,200,200,0.4)'),   # define el estilo de las lineas
    hoverinfo='none',                                     # desactiva el hover para las lineas
    mode='lines',                                         # especifica que este trazado es de lineas
    showlegend=False                                      # no muestra este trazado en la leyenda
)

fig = go.Figure(data=[edge_trace])                        # crea la figura inicial solo con las lineas

for i in range(N_SUBCLUSTERS):                            # itera sobre cada cluster para dibujar los puntos
    mascara_cluster = (subtypes == i)                     # selecciona los puntos de este cluster
    coordenadas_cluster = coords[mascara_cluster]         # obtiene sus coordenadas
    imagenes_hover_cluster = np.array(hover_imgs)[mascara_cluster] # selecciona sus imagenes correspondientes
    indices_cluster = np.where(mascara_cluster)[0]        # obtiene sus indices
    
    textos_hover = [f"Index: {idx}<br>Categoria: {subtype_names[i]}" for idx in indices_cluster] # crea el texto para el hover de cada punto
    
    fig.add_trace(go.Scatter(                             # anade un nuevo trazado de puntos para este cluster
        x=coordenadas_cluster[:, 0],                      # coordenadas X de los puntos
        y=coordenadas_cluster[:, 1],                      # coordenadas Y de los puntos
        mode='markers',                                   # especifica que es un trazado de puntos (marcadores)
        marker=dict(size=5, color=color_map[i], line=dict(width=0.5, color='white')), # define el estilo de los puntos
        hoverinfo='text',                                 # especifica que el hover mostrara el 'hovertext'
        hovertext=textos_hover,                           # asigna los textos de hover
        customdata=imagenes_hover_cluster,                # guarda la imagen en base64 en 'customdata' para el callback
        name=subtype_names[i]                             # asigna el nombre del cluster para la leyenda
    ))

fig.add_trace(go.Scatter(                                 # anade un trazado especial para los nodos centrales
    x=coords[nodos_centrales, 0],                         # coordenadas X de los nodos centrales
    y=coords[nodos_centrales, 1],                         # coordenadas Y de los nodos centrales
    mode='markers',                                       # modo de puntos
    marker=dict(size=8, color='white', line=dict(width=1.5, color='black')), # estilo de los nodos centrales (mas grandes y blancos)
    hoverinfo='none',                                     # sin hover para los nodos centrales
    showlegend=False                                      # no los muestra en la leyenda
))

fig.update_layout(                                        # actualiza el diseno general del grafico
    title="Vestidos - Subcluster",                        # titulo del grafico
    paper_bgcolor='black',                                # color de fondo de toda la figura
    plot_bgcolor='black',                                 # color de fondo del area del grafico
    xaxis=dict(showgrid=False, zeroline=False, visible=False), # oculta el eje X y sus lineas
    yaxis=dict(showgrid=False, zeroline=False, visible=False), # oculta el eje Y y sus lineas
    hovermode='closest',                                  # activa el hover para el punto mas cercano al cursor
    legend=dict(font=dict(color='white'), title_text='Legenda') # define el estilo de la leyenda
)

app = dash.Dash(__name__)                                 # crea la aplicacion Dash

app.layout = html.Div(style={'backgroundColor':'#111', 'height':'100vh', 'padding':'10px'}, children=[ # contenedor principal de la app
    html.H3("Vestidos - Hover para ver imagen", style={'color':'white'}), # titulo de la pagina
    
    html.Div(style={'backgroundColor':'#111', 'padding':'10px'}, children=[ # contenedor para el grafico y el panel
        dcc.Graph(                                        # componente para mostrar la figura de Plotly
            id='graph',                                   # ID para referenciarlo en los callbacks
            figure=fig,                                   # la figura a mostrar
            style={'width':'70vw','height':'80vh','display':'inline-block'} # estilo CSS
        ),
        
        html.Div(id='panel',                              # contenedor para el panel lateral
                 style={'width':'28vw', 'display':'inline-block', 'verticalAlign':'top', 'paddingLeft':'20px'},
                 children=[
                     html.P("Pasa el cursor sobre un punto para ver la imagen aqui.", style={'color':'white'}), # texto de instruccion
                     html.Img(id='hover-image', src='', style={'width':'300px', 'height':'300px', 'display':'block', 'marginTop':'10px', 'border':'1px solid #ccc'}) # la imagen que se actualizara
                 ])
    ])
])

@app.callback(                                            # decorador que define la interactividad
    Output('hover-image', 'src'),                         # la salida es el atributo 'src' de la imagen
    Input('graph', 'hoverData')                           # la entrada son los datos del hover del grafico
)
def display_hover_image(hoverData):                       # funcion que se ejecuta cuando el usuario hace hover
    if not hoverData:                                     # si no hay datos de hover (el cursor no esta sobre un punto)
        return ''                                         # no devuelve ninguna imagen
    try:
        img_src = hoverData['points'][0].get('customdata', '') # extrae la imagen en base64 del 'customdata' del punto
        return img_src                                    # devuelve la imagen para actualizar el 'src'
    except (KeyError, IndexError):                        # si hay algun error al extraer los datos
        return ''                                         # no devuelve nada

if __name__ == "__main__":                                # si el script se ejecuta directamente
    print("Iniciando app Dash...")                        # imprime un mensaje de inicio
    app.run(debug=True, host="127.0.0.1", port=8050, use_reloader=False) # inicia el servidor de la aplicacion Dash