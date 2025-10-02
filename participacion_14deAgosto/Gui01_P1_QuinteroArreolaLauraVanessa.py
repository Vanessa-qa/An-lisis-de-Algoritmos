import tkinter as tk

root = tk.Tk()
root.title("Soy una ventana GUI")
root.geometry("500x500")

lbl = tk.Label(root, text="¡No le se al python!")
lbl.pack(pady=100)

lbl0 = tk.Checkbutton(root,text= "XD")
lbl0.pack(pady=50)

root.mainloop()
