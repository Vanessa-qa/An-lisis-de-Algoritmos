import tkinter as tk

def saludar():
    nombre = entrada.get().strip()
    if not nombre:
        nombre = "mundo"
    lbl.config(text=f"Hola Compa, {nombre} 👋")

root = tk.Tk()
root.title("Saludador de Compas")
root.geometry("1000x300")
root.configure(background="purple")

lbl = tk.Label(root, text="Eh compa, Escribe tu nombre y presiona el botón", font=("Arial", 15, "bold"))
lbl.pack(pady=10)

entrada = tk.Entry(root)
entrada.pack(pady=5)

btn = tk.Button(root, text="Saludar", font=("Courier New", 10), command=saludar)
btn.pack(pady=10)

root.mainloop()