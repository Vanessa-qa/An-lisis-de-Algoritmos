import sys
import re
import requests
import io

from PySide6.QtCore import (
    Qt, QThread, Signal, Slot, QByteArray, QSize
)
from PySide6.QtGui import (
    QPixmap, QFont, QColor, QPalette, QPainter
)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QLineEdit,
    QPushButton, QVBoxLayout, QHBoxLayout, QFormLayout,
    QGridLayout, QScrollArea, QFrame, QSizePolicy,
    QSpacerItem
)

# INICIO DE HOJA DE ESTILOS QSS

# Definir paleta de colores 
DARK_PURPLE = "#1a0f26" # Morado
NEON_BLUE = "#04acac"   # Azul 
LIGHT_GRAY = "#cccccc"  # Texto claro
DARK_GRAY = "#2a2138"   # Fondo de inputs

# estilos QSS
STYLESHEET = f"""
    QWidget {{
        background-color: {DARK_PURPLE};
        color: {LIGHT_GRAY};
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 14px;
    }}
    QMainWindow {{
        border: 1px solid {NEON_BLUE};
    }}
    QLabel#TitleLabel {{
        color: {NEON_BLUE};
        font-size: 28px;
        font-weight: bold;
        qproperty-alignment: 'AlignCenter';
    }}
    QLabel#HeaderLabel {{
        color: {NEON_BLUE};
        font-size: 18px;
        font-weight: bold;
        margin-top: 10px;
    }}
    QLineEdit {{
        background-color: {DARK_GRAY};
        border: 1px solid {NEON_BLUE};
        border-radius: 5px;
        padding: 8px;
        color: white;
        font-size: 15px;
    }}
    QLineEdit:focus {{
        border: 2px solid white;
    }}
    QPushButton {{
        background-color: {NEON_BLUE};
        color: {DARK_PURPLE};
        font-size: 16px;
        font-weight: bold;
        border-radius: 5px;
        padding: 10px 15px;
        min-width: 120px;
    }}
    QPushButton:hover {{
        background-color: #33ffff; /* Un poco más brillante */
    }}
    QPushButton:disabled {{
        background-color: #555;
        color: #999;
    }}
    QLabel#StatusLabel {{
        color: {LIGHT_GRAY};
        font-size: 14px;
        qproperty-alignment: 'AlignCenter';
    }}
    QScrollArea {{
        border: 1px solid {NEON_BLUE};
        border-radius: 5px;
        background-color: {DARK_GRAY};
    }}
    #InfoWidget {{
        background-color: {DARK_GRAY}; /* Fondo del widget dentro del scroll */
    }}
    QLabel#InfoLabel {{
        background-color: transparent; /* Hereda del padre */
        color: {LIGHT_GRAY};
        padding: 10px;
    }}
    QLabel#GameImageLabel {{
        border: 1px solid {NEON_BLUE};
        border-radius: 5px;
        background-color: {DARK_GRAY};
        qproperty-alignment: 'AlignCenter';
        min-height: 200px; /* Altura mínima para la imagen */
    }}
    #PlatformBox {{
        margin-top: 10px;
    }}
"""
# FIN DE LA HOJA DE ESTILOS QSS

# INICIO DE CODIGO PARA ELEGIR BUILD

def LimpiarHTML(texto_html):
    """Funcion que elimina las etiquetas HTML"""
    # Reemplaza etiquetas de lista <li> por un guion y un salto de linea para formatear
    texto = texto_html.replace('<li>', '\n- ').replace('<br>', '\n')
    # Usa una expresion regular para encontrar y eliminar cualquier otra etiqueta HTML (<...>)
    limpio = re.sub(r'<.*?>', '', texto)
    # Elimina espacios o lineas en blanco al inicio y al final
    return limpio.strip()

def LocalizarJuego(nombre):
    """Funcion para buscar los juegos, pasamos el parametro"""
    url = "https://store.steampowered.com/api/storesearch/"
    parametros = {"term": nombre, "cc": "mx", "l": "spanish"}
    
    try:
        r = requests.get(url, params=parametros, timeout=10)
        r.raise_for_status()  # Lanza un error si la petición falla
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error de red en LocalizarJuego: {e}")
        return None

    if data.get("total", 0) == 0:
        return None
    
    item = data["items"][0]
    return {"appid": item["id"], "name": item["name"]}

def ObtenerDetalles(appid):
    """funcion para obtener los detalles mediante el id del juego"""
    url = f"https://store.steampowered.com/api/appdetails/"
    parametros = {"appids": appid, "cc": "mx", "l": "spanish"}
    
    try:
        r = requests.get(url, params=parametros, timeout=10)
        r.raise_for_status()
        data = r.json()
    except requests.exceptions.RequestException as e:
        print(f"Error de red en ObtenerDetalles: {e}")
        return None

    if not data.get(str(appid), {}).get("success", False):
        return None
    
    detalles = data[str(appid)]["data"]
    nombre = detalles.get("name", "Desconocido")
    precio = detalles.get("price_overview", {})
    
    if precio:
        precio_str = f'{precio.get("final_formatted", "desconocido")}'
    else:
        precio_str = "Gratis / no disponible"
    
    plataformas_dict = detalles.get("platforms", {})
    plataformas_str = ", ".join([k for k, v in plataformas_dict.items() if v])
    imagen_url = detalles.get("header_image", "")

    requisitos_min_html = detalles.get("pc_requirements", {}).get("minimum", "no disponible")
    requisitos_rec_html = detalles.get("pc_requirements", {}).get("recommended", "No disponible")

    cpu_min, gpu_min, ram_min = ObtenerRequisitos(requisitos_min_html)
    cpu_rec, gpu_rec, ram_rec = ObtenerRequisitos(requisitos_rec_html)

    return {
        "nombre": nombre,
        "precio": precio_str,
        "plataformas_str": plataformas_str,
        "plataformas_dict": plataformas_dict,
        "imagen_url": imagen_url,
        "requisitos_minimos": LimpiarHTML(requisitos_min_html),
        "requisitos_recomentados": LimpiarHTML(requisitos_rec_html),
        "cpu_min": cpu_min,
        "gpu_min": gpu_min,
        "ram_min": ram_min,
        "cpu_rec": cpu_rec,
        "gpu_rec": gpu_rec,
        "ram_rec": ram_rec
    }

def ObtenerRequisitos(texto):
    """funcion para obtener el gpu, cpu y ram de un juego"""
    cpu = None
    gpu = None
    ram = None
    
    if texto != "no disponible" and texto != "No disponible":
        texto_limpio = LimpiarHTML(texto)
        cpu_match = re.search(r"(?:Procesador|Processor|CPU):\s*([^\n]+)", texto_limpio, re.IGNORECASE)
        gpu_match = re.search(r"(?:Gráficos|Graphics|GPU|Tarjeta gráfica|Video Card):\s*([^\n]+)", texto_limpio, re.IGNORECASE)
        ram_match = re.search(r"(?:Memoria|Memory|RAM):\s*([^\n]+)", texto_limpio, re.IGNORECASE)
        
        if cpu_match:
            cpu = cpu_match.group(1).strip()
        if gpu_match:
            gpu = gpu_match.group(1).strip()
        if ram_match:
            ram = ram_match.group(1).strip()
            
    return cpu, gpu, ram

def CargarComponentes():
    """devuelve listas de cpus, gpus y precios para ram en MXN"""
    cpus = [
        {"name":"Intel Core i5-2500","score":5200,"price":1200},
        {"name":"Intel Core i7-6700","score":8400,"price":2500},
        {"name":"AMD Ryzen 5 3600","score":13000,"price":4000},
        {"name":"AMD Ryzen 5 5600","score":18000,"price":6000},
        {"name":"Intel Core i5-10400","score":11000,"price":2200}
    ]
    gpus = [
        {"name":"NVIDIA GeForce GTX 970","score":6700,"price":2000},
        {"name":"NVIDIA GeForce GTX 1060","score":8000,"price":3200},
        {"name":"NVIDIA GeForce RTX 2060","score":15000,"price":5000},
        {"name":"NVIDIA GeForce RTX 3060","score":22000,"price":9000},
        {"name":"NVIDIA GeForce GTX 1650","score":6000,"price":2200}
    ]
    ram_options = {8:800, 16:1500, 32:3000} #precio aproximado en MXN
    return cpus, gpus, ram_options

def BuscarComponentes(lista, nombre):
    """busca componente por coincidencia simple"""
    if not nombre:
        return None
    nombre_l = nombre.lower()
    mejores = []
    for c in lista:
        n = c["name"].lower()
        if nombre_l in n or n in nombre_l:
            mejores.append(c)
    if mejores:
        # elegir el de mayor score entre coincidencias
        mejores.sort(key=lambda x: x["score"], reverse=True)
        return mejores[0]
    return None

def Build(presupuesto, cpu_req_name, gpu_req_name):
    """Recomienda una build basada en presupuesto y requisitos"""
    cpus, gpus, ram_options = CargarComponentes()
    cpu_obj = BuscarComponentes(cpus, cpu_req_name)
    gpu_obj = BuscarComponentes(gpus, gpu_req_name)
    cpu_target = cpu_obj["score"] if cpu_obj else 0
    gpu_target = gpu_obj["score"] if gpu_obj else 0

    gpu_ram_combos = []
    for gpu in gpus:
        for ram_size, ram_price in ram_options.items():
            price = gpu["price"] + ram_price
            partial_score = (0.6 * gpu["score"]) + (0.1 * (ram_size * 1000))
            gpu_ram_combos.append({"gpu": gpu, "ram_size": ram_size, "ram_price": ram_price, "price": price, "partial_score": partial_score})

    gpu_ram_combos.sort(key=lambda x: x["price"])

    prefix_best = []
    best_combo = None
    for combo in gpu_ram_combos:
        if best_combo is None or combo["partial_score"] > best_combo["partial_score"]:
            best_combo = combo
        prefix_best.append(best_combo)

    import bisect
    mejores = None
    mejor_val = -1
    prices = [c["price"] for c in gpu_ram_combos]

    for cpu in cpus:
        remaining = presupuesto - cpu["price"]
        if remaining < 0:
            continue
        idx = bisect.bisect_right(prices, remaining) - 1
        if idx >= 0:
            best_partial = prefix_best[idx]
            total_price = cpu["price"] + best_partial["price"]
            score = (0.3 * cpu["score"]) + best_partial["partial_score"]
            val = score / max(1, total_price)
            cumple_objetivo = (cpu["score"] >= cpu_target) and (best_partial["gpu"]["score"] >= gpu_target)
            if cumple_objetivo:
                val *= 1.15
            if val > mejor_val:
                mejor_val = val
                mejores = {"cpu": cpu, "gpu": best_partial["gpu"], "ram": {"size": best_partial["ram_size"], "price": best_partial["ram_price"]}, "total": total_price}

    if not mejores:
        cpu_choice = min(cpus, key=lambda x: x["price"]) if cpus else None
        gpu_choice = min(gpus, key=lambda x: x["price"]) if gpus else None
        ram_size, ram_price = min(ram_options.items(), key=lambda x: x[1])
        ram_choice = {"size": ram_size, "price": ram_price}
        total_price = (cpu_choice["price"] if cpu_choice else 0) + (gpu_choice["price"] if gpu_choice else 0) + ram_choice["price"]
        mejores = {"cpu": cpu_choice, "gpu": gpu_choice, "ram": ram_choice, "total": total_price}

    # Añadimos el presupuesto original para mostrarlo
    mejores["presupuesto"] = presupuesto
    return mejores

# FIN DE CODIGO PARA ELEGIR BUILD

# GUI EN PYSIDE6
# Hilo de Trabajo (Worker)
class Worker(QThread):
    """
    Hilo de trabajo para ejecutar las tareas de red (requests)
    y la logica de build sin congelar la GUI.
    """
    # Señal que emite un diccionario con los resultados
    result_ready = Signal(object) 
    # Señal que emite el QPixmap de la imagen descargada
    image_ready = Signal(QPixmap)
    # Señal para emitir mensajes de error
    error = Signal(str)

    def __init__(self, game_name, budget):
        super().__init__()
        self.game_name = game_name
        self.budget = budget

    @Slot()
    def run(self):
        """
        Aqui se ejecuta la logica de busqueda
        """
        try:
            juego_encontrado = LocalizarJuego(self.game_name)
            
            if not juego_encontrado:
                self.error.emit("No se encontro el juego")
                return

            detalles = ObtenerDetalles(juego_encontrado["appid"])
            
            if not detalles:
                self.error.emit("No se pudieron obtener los detalles del juego.")
                return

            # Ejecutar la logica de la build
            resultado_build = Build(self.budget, detalles["cpu_rec"], detalles["gpu_rec"])
            
            # Combinar todos los resultados en un solo objeto
            resultados_completos = {
                "detalles": detalles,
                "build": resultado_build
            }

            # Emitir los resultados de texto
            self.result_ready.emit(resultados_completos)

            # --- Manejo de la imagen ---
            imagen_url = detalles.get("imagen_url")
            if imagen_url:
                try:
                    # Descargar la imagen
                    respuesta_img = requests.get(imagen_url, timeout=10)
                    respuesta_img.raise_for_status()
                    
                    # Cargar la imagen en un QPixmap
                    pixmap = QPixmap()
                    pixmap.loadFromData(respuesta_img.content)
                    
                    if not pixmap.isNull():
                        # Emitir la imagen
                        self.image_ready.emit(pixmap)
                
                except requests.exceptions.RequestException as e:
                    print(f"Error descargando la imagen: {e}")
                    # No emitimos error aquí, la app puede funcionar sin imagen

        except Exception as e:
            # Captura cualquier otro error inesperado
            self.error.emit(f"Error inesperado: {str(e)}")


# --- Ventana Principal ---
class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicacion.
    """
    
    # --- Datos SVG para los logos de plataformas ---
    # (SVG simples para Windows, Apple/Mac, y Linux/Tux)
    SVG_WINDOWS = """
    <svg fill="#00ffff" height="32px" width="32px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
	 viewBox="0 0 47.607 47.607" xml:space="preserve">
    <g>
	<path d="M20.482,22.784H2.421V4.723h18.061V22.784z M20.482,42.884H2.421V24.823h18.061V42.884z M45.186,22.784H27.124V4.723
		h18.061V22.784z M45.186,42.884H27.124V24.823h18.061V42.884z"/>
    </g>
    </svg>
    """
    SVG_MAC = """
    <svg fill="#00ffff" height="32px" width="32px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
	 viewBox="0 0 210 210" xml:space="preserve">
    <path d="M166.2,126.8c-1.8,7.3-4.9,13.8-9.1,19.3c-4.9,6.5-11.2,11.8-18.7,15.8c-7.3,3.9-15.3,5.8-23.9,5.8
	c-7.6,0-15.6-2.2-23.9-6.6c-8.1-4.2-14.7-10-19.8-17.1c-10.4-14.6-15.7-31.9-15.7-51.7c0-10.1,1.7-19.4,5.1-27.9
	c4.7-11.7,11.8-20.8,21.1-27.1c9.2-6.3,19.6-9.5,31.1-9.5c8.3,0,16.5,2.4,24.5,7.1c7.3,4.3,13,10.2,17.1,17.4
	c-8.8,5.4-13.2,10.7-13.2,15.8c0,4.2,1.3,7.9,3.8,11.2c2.5,3.2,5.7,5.5,9.6,6.9c4.2,1.4,8.6,2.1,13.2,2.1
	c1.1,0,2.4-0.1,3.8-0.2c-0.1,4-1.1,8.1-2.9,12.2C169,119.8,167.9,123.5,166.2,126.8z M145.4,0c-11,0.2-21.6,4.4-29.8,12.2
	c-2.9,2.8-5.4,6.2-7.6,10c-3.1,5.5-5.1,11.4-6,17.7c-0.8,5.4-1.2,10.8-1.2,16.3c0,6.2,0.8,12.2,2.5,17.7
	c-13.4-3.1-25.1-0.2-35,8.7c-9.1,8.1-15.3,18.8-18.7,31.9c-3.4,13.1-3,26.7,1.2,40.7c5.1,16.4,14,30.3,26.4,41.5
	c8.2,7.4,17.6,12.9,27.9,16.5c10,3.6,20.4,5.4,31.1,5.4c10.3,0,20.4-1.8,30.3-5.3c10.3-3.6,19.6-9,27.9-16.1
	c8.4-7.2,15-16.2,19.8-26.7c-17,9.3-35,3.5-44.1-17.4c-3.9-8.8-3.9-18.4,0-28.7c5.6-14.8,16.2-24.9,31.9-30.3
	c0.9-2.9,1.4-5.8,1.4-8.8c0-11.8-3.6-22.9-10.7-33.3C167.6,4.1,157.1-0.2,145.4,0z"/>
    </svg>
    """
    SVG_LINUX = """
    <svg fill="#00ffff" height="32px" width="32px" version="1.1" id="Layer_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
	 viewBox="0 0 286.03 286.03" xml:space="preserve">
    <g>
	<path d="M211.332,20.16c-17.764-6.6-35.124-2.404-49.1,11.332c-1.396,1.4-2.732,2.848-4.04,4.308
		c-1.308-1.46-2.644-2.908-4.04-4.308c-13.976-13.736-31.336-17.932-49.1-11.332C87.288,27.028,74.68,41.344,74.68,58.08
		c0,13.432,6.56,25.46,16.708,32.84c-3.136,1.868-6.104,4.02-8.84,6.42c-15.156,13.344-24.112,32.324-24.112,52.88
		c0,20.108,8.596,38.8,23.12,52.012c-1.568,2.78-2.736,5.748-3.52,8.84c-5.184,20.32-23.7,56.556-23.7,56.556
		s19.988,2.44,40.156-11.956c4.04-2.88,7.664-6.224,10.828-9.98c25.32,18.06,58.82,18.06,84.14,0
		c3.164,3.756,6.788,7.1,10.828,9.98c20.168,14.396,40.156,11.956,40.156,11.956s-18.516-36.236-23.7-56.556
		c-0.784-3.092-1.952-6.06-3.52-8.84c14.524-13.212,23.12-31.904,23.12-52.012c0-20.556-8.956-39.536-24.112-52.88
		c-2.736-2.4-5.704-4.552-8.84-6.42C204.792,83.54,211.352,71.512,211.352,58.08C211.352,41.344,198.744,27.028,211.332,20.16z
		 M111.42,88.988c-8.42,0-15.244-6.824-15.244-15.244c0-8.42,6.824-15.244,15.244-15.244c8.42,0,15.244,6.824,15.244,15.244
		C126.664,82.164,119.84,88.988,111.42,88.988z M174.612,88.988c-8.42,0-15.244-6.824-15.244-15.244
		c0-8.42,6.824-15.244,15.244-15.244c8.42,0,15.244,6.824,15.244,15.244C189.856,82.164,183.032,88.988,174.612,88.988z"/>
    </g>
    </svg>
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recomendador de Builds (Steam)")
        self.setGeometry(100, 100, 1000, 700) # Tamaño inicial

        # Hilo de trabajo
        self.worker = None

        # Aplicar el estilo QSS desde la constante global
        self.setStyleSheet(STYLESHEET)

        # Widget central y layout principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 1. Sección de Inputs
        self.create_input_section()
        
        # 2. Separador
        self.separator = QFrame()
        self.separator.setFrameShape(QFrame.Shape.HLine)
        # Usamos la variable global para el estilo del separador
        self.separator.setStyleSheet(f"background-color: {NEON_BLUE}; height: 2px;")
        self.separator.hide() # Oculto al inicio
        self.main_layout.addWidget(self.separator)

        # 3. Seccion de Resultados
        self.create_results_section()

        # Añadir un espaciador al final
        self.main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def create_input_section(self):
        """Crea los widgets para la entrada de datos."""
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        title_label = QLabel("Recomendador de Builds")
        title_label.setObjectName("TitleLabel")
        input_layout.addWidget(title_label)

        # Formulario para juego y presupuesto
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(20, 20, 20, 20)

        self.game_input = QLineEdit()
        self.game_input.setPlaceholderText("Escribe el nombre del juego (ej: Hollow Knight: Silksong)")
        form_layout.addRow(QLabel("Juego:"), self.game_input)

        self.budget_input = QLineEdit()
        self.budget_input.setPlaceholderText("Tu presupuesto en MXN (ej: 15000)")
        form_layout.addRow(QLabel("Presupuesto:"), self.budget_input)

        input_layout.addLayout(form_layout)

        # Boton de busqueda
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        self.search_button = QPushButton("Buscar Juego")
        self.search_button.clicked.connect(self.start_search)
        button_layout.addWidget(self.search_button)
        button_layout.addStretch()
        input_layout.addLayout(button_layout)

        # Etiqueta de estado
        self.status_label = QLabel()
        self.status_label.setObjectName("StatusLabel")
        input_layout.addWidget(self.status_label)

        self.main_layout.addWidget(input_widget)

    def create_results_section(self):
        """Crea los widgets para mostrar los resultados."""
        self.results_widget = QWidget()
        results_layout = QGridLayout(self.results_widget)
        results_layout.setSpacing(20)
        results_layout.setContentsMargins(10, 20, 10, 10)

        # Columna Izquierda: Imagen
        self.game_image_label = QLabel("Imagen del juego...")
        self.game_image_label.setObjectName("GameImageLabel")
        self.game_image_label.setMinimumSize(460, 215)
        self.game_image_label.setMaximumSize(460, 215)
        results_layout.addWidget(self.game_image_label, 0, 0, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)
        
        # Plataformas (debajo de la imagen)
        self.platform_box = QWidget()
        self.platform_box.setObjectName("PlatformBox")
        self.platform_layout = QHBoxLayout(self.platform_box)
        self.platform_layout.setSpacing(15)
        self.platform_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        results_layout.addWidget(self.platform_box, 1, 0, Qt.AlignmentFlag.AlignCenter)

        # Columna Derecha: Informacion
        self.info_scroll_area = QScrollArea()
        self.info_scroll_area.setWidgetResizable(True)
        
        self.info_widget_container = QWidget()
        self.info_widget_container.setObjectName("InfoWidget")
        info_layout = QVBoxLayout(self.info_widget_container)
        
        self.game_info_label = QLabel("Aqui se mostrara la informacion del juego...")
        self.game_info_label.setObjectName("InfoLabel")
        self.game_info_label.setTextFormat(Qt.TextFormat.RichText)
        self.game_info_label.setWordWrap(True)
        self.game_info_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        info_layout.addWidget(self.game_info_label)
        self.info_scroll_area.setWidget(self.info_widget_container)
        
        results_layout.addWidget(self.info_scroll_area, 0, 1, 2, 1)

        # Ajustar el tamaño de las columnas
        results_layout.setColumnStretch(0, 1) # Columna imagen (más pequeña)
        results_layout.setColumnStretch(1, 2) # Columna info (más grande)
        
        self.main_layout.addWidget(self.results_widget)
        self.results_widget.hide()

    def start_search(self):
        """Inicia el proceso de busqueda en el hilo de trabajo."""
        game_name = self.game_input.text().strip()
        budget_str = self.budget_input.text().strip()

        if not game_name:
            self.status_label.setText("Por favor, escribe el nombre de un juego.")
            return

        try:
            budget = int(float(budget_str))
        except ValueError:
            self.status_label.setText("Por favor, introduce un presupuesto valido (ej: 15000).")
            return

        # Preparar la UI para la busqueda
        self.search_button.setEnabled(False)
        self.search_button.setText("Buscando...")
        self.status_label.setText("Contactando a la API de Steam...")
        self.results_widget.hide()
        self.separator.hide()
        
        # Limpiar resultados anteriores
        self.clear_layout(self.platform_layout)
        self.game_image_label.setText("Cargando imagen...")
        self.game_info_label.setText("Buscando informacion...")

        # Iniciar el hilo de trabajo
        self.worker = Worker(game_name, budget)
        self.worker.result_ready.connect(self.show_results)
        self.worker.image_ready.connect(self.show_game_image)
        self.worker.error.connect(self.show_error)
        # Limpiar el hilo cuando termine
        self.worker.finished.connect(self.worker.deleteLater) 
        self.worker.start()

    @Slot(object)
    def show_results(self, results):
        """Muestra los resultados de texto en la GUI."""
        self.status_label.setText("¡Juego encontrado!")
        self.search_button.setEnabled(True)
        self.search_button.setText("Buscar")

        detalles = results["detalles"]
        build = results["build"]

        # Formatear el texto de informacion con HTML
        # Usamos la variable global NEON_BLUE
        info_html = f"""
        <h2 style="color: {NEON_BLUE};">{detalles['nombre']}</h2>
        <p><strong>Precio:</strong> {detalles['precio']}</p>
        
        <h3 style="color: {NEON_BLUE}; margin-top: 15px;">Requisitos Mínimos:</h3>
        <p style="white-space: pre-wrap; margin-left: 10px;">{detalles['requisitos_minimos'].replace('<', '&lt;')}</p>
        
        <h3 style="color: {NEON_BLUE}; margin-top: 15px;">Requisitos Recomendados:</h3>
        <p style="white-space: pre-wrap; margin-left: 10px;">{detalles['requisitos_recomentados'].replace('<', '&lt;')}</p>
        
        <hr style="border: 1px solid {NEON_BLUE};">
        
        <h2 style="color: {NEON_BLUE};">Build Sugerida (Presupuesto: ${build['presupuesto']})</h2>
        <p><strong>CPU:</strong> {build['cpu']['name']} | Precio aprox: ${build['cpu']['price']}</p>
        <p><strong>GPU:</strong> {build['gpu']['name']} | Precio aprox: ${build['gpu']['price']}</p>
        <p><strong>RAM:</strong> {build['ram']['size']}GB | Precio aprox: ${build['ram']['price']}</p>
        <h3 style="color: white;">Precio Total Aprox: ${build['total']} MXN</h3>
        """
        self.game_info_label.setText(info_html)
        
        # --- Mostrar Logos de Plataformas ---
        self.clear_layout(self.platform_layout) # Limpiar logos anteriores
        platforms = detalles["plataformas_dict"]
        
        if platforms.get("windows", False):
            self.platform_layout.addWidget(self.create_svg_icon(self.SVG_WINDOWS))
        if platforms.get("mac", False):
            self.platform_layout.addWidget(self.create_svg_icon(self.SVG_MAC))
        if platforms.get("linux", False):
            self.platform_layout.addWidget(self.create_svg_icon(self.SVG_LINUX))

        # Mostrar la seccion de resultados
        self.separator.show()
        self.results_widget.show()

    @Slot(QPixmap)
    def show_game_image(self, pixmap):
        """Muestra la imagen del juego descargada."""
        # Escalar la imagen para que quepa en el QLabel
        scaled_pixmap = pixmap.scaled(
            self.game_image_label.size(), 
            Qt.AspectRatioMode.KeepAspectRatioByExpanding,
            Qt.TransformationMode.SmoothTransformation
        )
        self.game_image_label.setPixmap(scaled_pixmap)

    @Slot(str)
    def show_error(self, message):
        """Muestra un mensaje de error."""
        self.status_label.setText(message)
        self.search_button.setEnabled(True)
        self.search_button.setText("Buscar")
        self.results_widget.hide()
        self.separator.hide()

    # Funciones de Utilidad
    def clear_layout(self, layout):
        """Limpia todos los widgets de un layout."""
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def create_svg_icon(self, svg_data, size=32):
        """Crea un QLabel con un icono a partir de datos SVG."""
        byte_array = QByteArray(svg_data.encode('utf-8'))
        renderer = QSvgRenderer(byte_array)
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        painter.end()
        
        icon_label = QLabel()
        icon_label.setPixmap(pixmap)
        icon_label.setFixedSize(size, size)
        return icon_label

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    font = QFont("Segoe UI")
    app.setFont(font)

    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())