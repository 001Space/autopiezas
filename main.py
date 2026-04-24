import pandas as pd
import tkinter as tk
from tkinter import messagebox

ARCHIVO_STOCK = "autopiezas.beta.xlsx"
ARCHIVO_SABO = "sabo.xlsx"

def cargar_datos():
    try:
        # Cargar stock
        stock_df = pd.read_excel(ARCHIVO_STOCK)
        stock_df.columns = stock_df.columns.str.strip()
        stock_df["id"] = stock_df["id"].astype(str)

        # Cargar consumo
        consumo_df = pd.read_excel(ARCHIVO_SABO)
        consumo_df.columns = consumo_df.columns.str.strip()
        consumo_df["id"] = consumo_df["id"].astype(str)

        # Verificar columnas obligatorias
        columnas_requeridas = {"id", "cantidad"}

        if not columnas_requeridas.issubset(consumo_df.columns):
            faltantes = columnas_requeridas - set(consumo_df.columns)
            raise ValueError(
                f"Faltan columnas en {ARCHIVO_SABO}: {', '.join(faltantes)}"
            )

        return stock_df, consumo_df

    except FileNotFoundError as e:
        messagebox.showerror(
            "Archivo no encontrado",
            f"No se encontró el archivo:\n{e.filename}"
        )
        exit()

    except Exception as e:
        messagebox.showerror(
            "Error al cargar datos",
            str(e)
        )
        exit()
        
df_stock, df_consumo = cargar_datos()   

def obtener_consumo_total(id_producto):
    consumo = df_consumo [ df_consumo ["id"].str.lower() == id_producto.lower()]

    if ARCHIVO_SABO.empy:
        return 0
    return consumo["cantidad"].sum()

def buscar_producto(id_producto):
    producto = df_stock [ df_stock["id"].str.lower() == id_producto.lower()]
    
    if producto.empty:
        return None
    
    return producto.iloc[0]

def calcular_reposicion(stock_actual, consumo_total):
    return max (0, round(consumo_total - stock_actual))


def  calcular():
    id_producto = entry_id.get().strip()
   
    if not id_producto:
       messagebox.showwarning(
           "SIN ID", "Ingrese ID de prodcuto"
           
       )
       return

    producto = buscar_producto(id_producto)
    if producto is None:
        resultado.set("Producto no encontrado")
        return
    stock_actual = producto["stock_fis"] - producto["stock_res"]
    consumo_total = obtener_consumo_total(id_producto)
    cantidad_pedir = calcular_reposicion(stock_actual, consumo_total)

    resultado.set(f"Producto: {producto['descripcion']}\n" f"Stock actual: {stock_actual}\n" f"Consumo total: {consumo_total}\n" f"Pedir: {cantidad_pedir}")

def obtener_consumo_total(id_producto):
    consumos = df_consumo[
        df_consumo["id"].str.lower() == id_producto.lower()
    ]

    if consumos.empty:
        return 0

    consumos["cantidad"] = pd.to_numeric(
        consumos["cantidad"],
        errors="coerce"
    ).fillna(0)

    return consumos["cantidad"].sum()

#interfaz :p

ventana = tk.Tk()
ventana.title("Reposicion de Stock de Autopiezas")
ventana.geometry("500x350")
ventana.resizable(False, False)

tk.Label()  
ventana, text="ID del producto: ",
font= ("Arial", 12).pack(pady=10)

entry_id = tk.Entry(
    ventana, font=("Arial", 12), width=30
)

entry_id.pack()

tk.Buttom(
    ventana,
    text="Calcular Reposicitorio",
    command=calcular,
    font=("Arial", 12),
    bg="#4C7AAF",
    fg="white",
).pack (pady=20)

resultado = tk.StringVar()

tk.Label(
    ventana,
    textvariable=resultado,
    font=("Arial", 12),
    justify="left",
    wraplength=450
).pack(pady=10)

ventana.mainloop()