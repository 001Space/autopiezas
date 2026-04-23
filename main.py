import pandas as pd
import tkinter as tk
from tkinter import messagebox

df = pd.read_excel("autopiezas.beta.xlsx")
df.columns = df.columns.str.strip()
df["id"] = df["id"].astype(str)

def calcular():
    id_producto = entry_id.get()
    try:
        consumo = float(entry_consumo.get())
    except:
        messagebox.showerror("Error", "El consumo debe ser un número")
        return

    for index, row in df.iterrows():
        if row["id"].lower() == id_producto.lower():
            stock = row["stock_fis"] - row["stock_res"]

            if stock > 0 and stock >= 2 * consumo:
                pedir = 0
            else:
                pedir = max(0, 2 * consumo - stock)

            resultado.set(f"Pedir: {pedir}")
            return

    resultado.set("Producto no encontrado")

ventana = tk.Tk()
ventana.title("Calculadora de Stock")
ventana.geometry("300x200")

tk.Label(ventana, text="ID del producto").pack()
entry_id = tk.Entry(ventana)
entry_id.pack()

tk.Label(ventana, text="Consumo").pack()
entry_consumo = tk.Entry(ventana)
entry_consumo.pack()

tk.Button(ventana, text="Calcular", command=calcular).pack(pady=10)

resultado = tk.StringVar()
tk.Label(ventana, textvariable=resultado, font=("Arial", 12)).pack()

ventana.mainloop()