import heapq
from collections import Counter
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import os
import shutil
import sys
import subprocess

# Creamos la clase nodo, para los nodos del arbol
class NodoArbol:
    def __init__(self, caracter, frecuencia):
        self.caracter = caracter
        self.frecuencia = frecuencia
        self.izquierda = None
        self.derecha = None

    # Comparamos la prioridad segun la frecuencia
    def __lt__(self, otro):
        return self.frecuencia < otro.frecuencia

# Creamos el arbol
def arbol_binario(nodo_raiz):
    resultado = {}

    # Recorremos el arbol para saber donde colocar el nodo
    def recorrer_arbol(nodo_actual, codigo_actual):
        if nodo_actual is None:
            return

        # Si es una hoja
        if nodo_actual.caracter is not None:
            # En caso de que el arbol tenga solo un nodo
            if codigo_actual == "":
                resultado[nodo_actual.caracter] = "0"
            else:
                resultado[nodo_actual.caracter] = codigo_actual
            return

        # Si es un nodo interno, seguimos recorriendo
        recorrer_arbol(nodo_actual.izquierda, codigo_actual + "0")
        recorrer_arbol(nodo_actual.derecha, codigo_actual + "1")

    recorrer_arbol(nodo_raiz, "")
    return resultado

# Creamos la codificacion huffman
def codificar_texto(texto, codigo):
    texto_codificado = []
    for caracter in texto:
        texto_codificado.append(codigo[caracter])
    
    # Se juntan los resultados de cada codificacion
    return "".join(texto_codificado)

# Decodificamos el texto usando el arbol
def decodificar_texto(texto_codificado, nodo_raiz):
    # En caso de que el arbol tenga solo un nodo
    if nodo_raiz.izquierda is None and nodo_raiz.derecha is None:
        return nodo_raiz.caracter * len(texto_codificado)

    texto_decodificado = []
    nodo_actual = nodo_raiz

    # Recorremos bit por bit el texto codificado
    for bit in texto_codificado:
        
        # Si es '0', vamos a la izquierda
        if bit == '0':
            nodo_actual = nodo_actual.izquierda
        # Si es '1', vamos a la derecha
        else: # bit == '1'
            nodo_actual = nodo_actual.derecha
        
        # Verificamos si llegamos a una HOJA
        if nodo_actual.caracter is not None:
            texto_decodificado.append(nodo_actual.caracter)
            nodo_actual = nodo_raiz

    # Se juntan los caracteres
    return "".join(texto_decodificado)


# Nombres de archivos
archivo_entrada = "input.txt"
archivo_codificado = "codificado.txt"
archivo_decodificado = "decodificado.txt"

# crear funciones auxiliares para GUI y guardado/lectura binaria
def pad_encoded_text(encoded):
    extra_padding = (8 - len(encoded) % 8) % 8
    encoded_padded = encoded + "0"*extra_padding
    return encoded_padded, extra_padding

def get_byte_array(padded_encoded):
    if len(padded_encoded) % 8 != 0:
        raise ValueError("Encoded text length not divisible by 8.")
    b_arr = bytearray()
    for i in range(0, len(padded_encoded), 8):
        byte = padded_encoded[i:i+8]
        b_arr.append(int(byte, 2))
    return bytes(b_arr)

def guardar_comprimido(ruta_salida, codes, padded_bytes, extra_padding, original_name):
    header = {
        "codes": codes,
        "padding": extra_padding,
        "original_name": original_name
    }
    header_json = json.dumps(header, ensure_ascii=False).encode('utf-8')
    header_len = len(header_json)
    with open(ruta_salida, "wb") as f:
        f.write(header_len.to_bytes(4, byteorder='big'))
        f.write(header_json)
        f.write(padded_bytes)

def leer_comprimido(ruta):
    with open(ruta, "rb") as f:
        header_len_bytes = f.read(4)
        if len(header_len_bytes) < 4:
            raise ValueError("Archivo comprimido corrupto o incompleto.")
        header_len = int.from_bytes(header_len_bytes, byteorder='big')
        header_json = f.read(header_len)
        header = json.loads(header_json.decode('utf-8'))
        compressed_bytes = f.read()
    return header, compressed_bytes

def bytes_a_bitstring(bts):
    bits = []
    for byte in bts:
        bits.append(f"{byte:08b}")
    return "".join(bits)

# crear arbol desde codigos para decodificar con tu funcion
def construir_arbol_desde_codigos(codes):
    root = NodoArbol(None, 0)
    for ch, code in codes.items():
        node = root
        for bit in code:
            if bit == '0':
                if node.izquierda is None:
                    node.izquierda = NodoArbol(None, 0)
                node = node.izquierda
            else:
                if node.derecha is None:
                    node.derecha = NodoArbol(None, 0)
                node = node.derecha
        node.caracter = ch
    return root

# crear GUI con botones comprimir y descomprimir y botones dinamicos de descarga
class HuffmanGUI:
    def __init__(self, root):
        self.root = root
        root.title("Compresor Huffman - GUI")
        root.geometry("920x600")
        self.file_path = None
        self.compressed_path = None
        self.decompressed_path = None
        self.last_freq = None
        self.last_codes = None
        self.btn_dynamic_comp = None
        self.btn_dynamic_desc = None
        self.dynamic_comp_mode = None  # 'compress' o 'download'
        self.dynamic_desc_mode = None  # 'decompress' o 'download'
        self.selected_bin_for_desc = None

        top = ttk.Frame(root, padding=8)
        top.pack(side=tk.TOP, fill=tk.X)

        # boton para seleccionar input (opcional, pero necesario si input.txt no esta en la carpeta)
        self.btn_select = ttk.Button(top, text="Seleccionar archivo .txt", command=self.seleccionar_archivo)
        self.btn_select.pack(side=tk.LEFT, padx=4)

        # boton descomprimir (queda visible siempre): ahora solo selecciona .bin
        self.btn_decompress = ttk.Button(top, text="Descomprimir", command=self.seleccionar_bin_para_descomprimir)
        self.btn_decompress.pack(side=tk.LEFT, padx=4)

        # boton mostrar codigos (opcional)
        self.btn_show = ttk.Button(top, text="Mostrar codigos", command=self.mostrar_codigos)
        self.btn_show.pack(side=tk.LEFT, padx=4)

        mid = ttk.Frame(root, padding=8)
        mid.pack(fill=tk.BOTH, expand=True)

        # cuadro de texto para informacion
        self.text_info = tk.Text(mid, wrap=tk.NONE)
        self.text_info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        yscroll = ttk.Scrollbar(mid, orient=tk.VERTICAL, command=self.text_info.yview)
        yscroll.pack(side=tk.LEFT, fill=tk.Y)
        self.text_info['yscrollcommand'] = yscroll.set

        # panel derecho donde apareceran los botones dinamicos (reemplaza la tabla)
        right = ttk.Frame(root, padding=8)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        lbl = ttk.Label(right, text="Acciones", font=("Segoe UI", 10, "bold"))
        lbl.pack(anchor=tk.NW)

        # panel donde apareceran los botones dinamicos
        self.buttons_panel = ttk.Frame(right)
        self.buttons_panel.pack(fill=tk.Y, pady=10)

        self.status = ttk.Label(root, text="Listo")
        self.status.pack(side=tk.BOTTOM, fill=tk.X)

    # funcion para escribir info en el cuadro de texto
    def escribir_info(self, texto):
        self.text_info.insert(tk.END, texto + "\n")
        self.text_info.see(tk.END)

    # seleccionar archivo (opcional)
    def seleccionar_archivo(self):
        path = filedialog.askopenfilename(filetypes=[("Text files","*.txt")])
        if not path:
            return
        self.file_path = path
        self.escribir_info(f"Archivo seleccionado: {path}")
        self.status.config(text=f"Archivo seleccionado: {os.path.basename(path)}")
        # quitar botones dinamicos si existian
        self._quitar_btns_dinamicos()
        # crear el boton dinamico de compresion (aparece al seleccionar .txt)
        basename = os.path.splitext(os.path.basename(path))[0]
        display_text = f"{basename}_compreso  [DESCARGAR]"
        self._crear_btn_dinamico_comp(display_text, path)

    # accion comprimir: lee input.txt (o archivo seleccionado si existe) y guarda .bin
    # nota: el boton dinamico realizara la compresion al primer click y luego permitira descarga
    def _crear_btn_dinamico_comp(self, display_text, entrada_path):
        # crear boton en modo 'compress' inicialmente
        self.dynamic_comp_mode = 'compress'
        self.btn_dynamic_comp = ttk.Button(self.buttons_panel, text=display_text, command=lambda: self._accion_dinamica_comp(entrada_path))
        self.btn_dynamic_comp.pack(pady=6, anchor=tk.N)

    # funcion dinamica para el boton compreso: comprime primero (sin preguntar) y luego cambia a modo descarga
    def _accion_dinamica_comp(self, entrada_path):
        # modo compress: crear .bin automaticamente en misma carpeta
        if self.dynamic_comp_mode == 'compress':
            entrada = entrada_path
            if not os.path.exists(entrada):
                messagebox.showwarning("Atencion", f"No se encontro el archivo de entrada: {entrada}")
                return
            try:
                with open(entrada, "r", encoding="utf-8") as f:
                    texto = f.read()
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo leer el archivo: {e}")
                return
            if texto == "":
                messagebox.showwarning("Atencion", "El archivo esta vacio.")
                return

            # contar frecuencias y construir arbol
            conteo = Counter(texto)
            cola = []
            for caracter, frecuencia in conteo.items():
                nodo = NodoArbol(caracter, frecuencia)
                heapq.heappush(cola, nodo)
            if len(cola) == 0:
                messagebox.showwarning("Atencion", "No hay caracteres para procesar.")
                return
            while len(cola) > 1:
                n1 = heapq.heappop(cola)
                n2 = heapq.heappop(cola)
                freq_sum = n1.frecuencia + n2.frecuencia
                padre = NodoArbol(None, freq_sum)
                padre.izquierda = n1
                padre.derecha = n2
                heapq.heappush(cola, padre)
            raiz = heapq.heappop(cola)

            # generar codigos y codificar
            codigos = arbol_binario(raiz)
            texto_cod = codificar_texto(texto, codigos)
            padded, extra = pad_encoded_text(texto_cod)
            bts = get_byte_array(padded)

            # guardar automaticamente en misma carpeta del archivo de entrada
            default_name = os.path.splitext(os.path.basename(entrada))[0] + ".bin"
            carpeta_salida = os.path.dirname(entrada) if os.path.dirname(entrada) else os.getcwd()
            ruta_salida = os.path.join(carpeta_salida, default_name)
            try:
                guardar_comprimido(ruta_salida, codigos, bts, extra, os.path.basename(entrada))
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el archivo comprimido: {e}")
                return

            # actualizar estado
            self.compressed_path = ruta_salida
            self.last_freq = dict(conteo)
            self.last_codes = codigos

            orig_size = os.path.getsize(entrada)
            comp_size = os.path.getsize(ruta_salida)
            bits_original = len(texto) * 8
            bits_compressed = len(texto_cod)
            ratio = comp_size / orig_size if orig_size>0 else 0

            self.escribir_info("=== Resultado de compresion ===")
            self.escribir_info(f"Archivo original: {entrada} ({orig_size} bytes)")
            self.escribir_info(f"Archivo comprimido (guardado automaticamente): {ruta_salida} ({comp_size} bytes)")
            self.escribir_info(f"Bits totales original: {bits_original} bits")
            self.escribir_info(f"Bits totales comprimido (sin header): {bits_compressed} bits")
            self.escribir_info(f"Padding agregado: {extra} bits")
            self.escribir_info(f"Relacion de compresion: {ratio:.3f}")
            avg_bits_symbol = bits_compressed / len(texto) if len(texto)>0 else 0
            self.escribir_info(f"Bits promedio por simbolo: {avg_bits_symbol:.3f}")
            self.status.config(text=f"Comprimido: {os.path.basename(ruta_salida)}")

            # cambiar modo del boton para que ahora sirva para 'download'
            self.dynamic_comp_mode = 'download'
            # boton queda con el mismo texto; su siguiente pulsacion abrira dialogo para guardar copia
        else:
            # modo download: pedir ruta donde guardar la copia
            if not self.compressed_path or not os.path.exists(self.compressed_path):
                messagebox.showwarning("Atencion", "No se encontro el archivo comprimido original.")
                return
            default_name = os.path.basename(self.compressed_path)
            destino = filedialog.asksaveasfilename(defaultextension=".bin", initialfile=default_name, filetypes=[("Huffman bin","*.bin")])
            if not destino:
                return
            try:
                shutil.copyfile(self.compressed_path, destino)
                messagebox.showinfo("Descarga completa", f"Archivo guardado en:\n{destino}")
                carpeta = os.path.dirname(destino)
                try:
                    if sys.platform.startswith("win"):
                        os.startfile(carpeta)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", carpeta])
                    else:
                        subprocess.run(["xdg-open", carpeta])
                except Exception:
                    pass
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la copia: {e}")

    # seleccionar .bin para descomprimir (solo selecciona, no procesa)
    def seleccionar_bin_para_descomprimir(self):
        path = filedialog.askopenfilename(filetypes=[("Huffman bin","*.bin")])
        if not path:
            return
        # guardar seleccion y crear boton dinamico para descompresion/descarga
        self.selected_bin_for_desc = path
        self.escribir_info(f"Archivo .bin seleccionado para descompresion: {path}")
        self.status.config(text=f"Bin seleccionado: {os.path.basename(path)}")
        # quitar botones dinamicos previos y crear nuevo boton
        self._quitar_btns_dinamicos()
        basename = os.path.splitext(os.path.basename(path))[0]
        display_text = f"{basename}_descompreso  [DESCARGAR]"
        # crear boton en modo 'decompress' inicialmente
        self.dynamic_desc_mode = 'decompress'
        self.btn_dynamic_desc = ttk.Button(self.buttons_panel, text=display_text, command=self._accion_dinamica_desc)
        self.btn_dynamic_desc.pack(pady=6, anchor=tk.N)

    # funcion dinamica para el boton descompreso: primero descomprime (al primer click), luego pasa a modo descarga
    def _accion_dinamica_desc(self):
        if self.dynamic_desc_mode == 'decompress':
            ruta = self.selected_bin_for_desc
            if not ruta or not os.path.exists(ruta):
                messagebox.showwarning("Atencion", "No se selecciono un archivo .bin valido.")
                return
            try:
                header, compressed = leer_comprimido(ruta)
                codes = header["codes"]
                padding = header.get("padding", 0)
                bits = bytes_a_bitstring(compressed)
                if padding:
                    bits = bits[:-padding]
                raiz = construir_arbol_desde_codigos(codes)
                texto_dec = decodificar_texto(bits, raiz)
                default_name = header.get("original_name", "descomprimido.txt")
                # guardar automaticamente el .txt descomprimido en la misma carpeta del .bin
                carpeta_bin = os.path.dirname(ruta) if os.path.dirname(ruta) else os.getcwd()
                ruta_salida = os.path.join(carpeta_bin, "decompressed_" + default_name)
                with open(ruta_salida, "w", encoding="utf-8") as f:
                    f.write(texto_dec)
                self.decompressed_path = ruta_salida
                self.escribir_info("=== Descompresion completada ===")
                self.escribir_info(f"Archivo leido: {ruta}")
                self.escribir_info(f"Archivo descomprimido (guardado automaticamente): {ruta_salida} ({len(texto_dec)} caracteres)")
                self.status.config(text=f"Descomprimido: {os.path.basename(ruta_salida)}")

                # cambiar modo del boton para que ahora permita descargar la copia
                self.dynamic_desc_mode = 'download'
                # boton mantiene el mismo texto; siguientes clicks abriran dialogo para guardar copia
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo descomprimir: {e}")
        else:
            # modo download: preguntar donde guardar copia del .txt descomprimido
            if not self.decompressed_path or not os.path.exists(self.decompressed_path):
                messagebox.showwarning("Atencion", "No se encontro el archivo descomprimido original.")
                return
            default_name = os.path.basename(self.decompressed_path)
            destino = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_name, filetypes=[("Text file","*.txt")])
            if not destino:
                return
            try:
                shutil.copyfile(self.decompressed_path, destino)
                messagebox.showinfo("Descarga completa", f"Archivo guardado en:\n{destino}")
                carpeta = os.path.dirname(destino)
                try:
                    if sys.platform.startswith("win"):
                        os.startfile(carpeta)
                    elif sys.platform == "darwin":
                        subprocess.run(["open", carpeta])
                    else:
                        subprocess.run(["xdg-open", carpeta])
                except Exception:
                    pass
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar la copia: {e}")

    # mostrar codigos en el cuadro de texto
    def mostrar_codigos(self):
        if not self.last_codes:
            messagebox.showinfo("Info", "No hay codigos generados aun. Comprime primero un archivo.")
            return
        self.escribir_info("=== Codigos Huffman ===")
        for ch, code in sorted(self.last_codes.items(), key=lambda x: (len(x[1]), x[1])):
            disp = ch
            if ch == "\n":
                disp = "\\n"
            elif ch == "\t":
                disp = "\\t"
            elif ch == " ":
                disp = "' '"
            self.escribir_info(f"'{disp}': {code}")

    # quitar botones dinamicos si existen
    def _quitar_btns_dinamicos(self):
        if self.btn_dynamic_comp is not None:
            try:
                self.btn_dynamic_comp.destroy()
            except:
                pass
            self.btn_dynamic_comp = None
            self.dynamic_comp_mode = None
        if self.btn_dynamic_desc is not None:
            try:
                self.btn_dynamic_desc.destroy()
            except:
                pass
            self.btn_dynamic_desc = None
            self.dynamic_desc_mode = None
            self.selected_bin_for_desc = None

def main():
    root = tk.Tk()
    app = HuffmanGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
