import pandas as pd
import tkinter as tk
from tkinter import messagebox
import os

# --- 1. CONFIGURACIÓN Y CARGA DE DATOS ---
ARCHIVO_STOCK = "autopiezas.beta.xlsx"
ARCHIVO_SABO = "sabo.xlsx"

def normalizar_id(valor):
    """Limpia el ID para que coincida siempre (quita espacios y .0)"""
    if pd.isna(valor): return ""
    return str(valor).strip().replace(".0", "").upper()

def cargar_datos():
    try:
        # Verificamos si los archivos existen
        if not os.path.exists(ARCHIVO_STOCK) or not os.path.exists(ARCHIVO_SABO):
            messagebox.showerror("Error", "No se encontraron los archivos Excel en la carpeta.")
            return None, None

        # Cargar Autopiezas
        df_a = pd.read_excel(ARCHIVO_STOCK)
        df_a.columns = df_a.columns.str.strip().str.lower()
        df_a["id"] = df_a["id"].apply(normalizar_id)

        # Cargar Sabo
        df_s = pd.read_excel(ARCHIVO_SABO)
        df_s.columns = df_s.columns.str.strip()
        # Renombramos según las columnas de tus imágenes
        df_s.rename(columns={"N° SABO": "id", "Consumo": "cantidad", "stock": "stock_sabo"}, inplace=True)
        df_s["id"] = df_s["id"].apply(normalizar_id)

        return df_a, df_s
    except Exception as e:
        messagebox.showerror("Error", f"Fallo al leer los archivos: {e}")
        return None, None

# Cargamos los DataFrames globalmente
df_stock, df_consumo = cargar_datos()

# --- 2. FUNCIONES DE BÚSQUEDA ---

def buscar_producto(id_producto):
    """Busca los datos en la tabla de autopiezas"""
    if df_stock is None: return None
    res = df_stock[df_stock["id"] == id_producto]
    return res.iloc[0] if not res.empty else None

def obtener_datos_sabo(id_producto):
    """Obtiene consumo y stock de la tabla Sabo"""
    if df_consumo is None: return 0, 0
    res = df_consumo[df_consumo["id"] == id_producto]
    if res.empty: return 0, 0
    
    # Sumamos por si hay filas duplicadas
    con = pd.to_numeric(res["cantidad"], errors='coerce').fillna(0).sum()
    stk = pd.to_numeric(res["stock_sabo"], errors='coerce').fillna(0).sum()
    return con, stk

# --- 3. LÓGICA DEL BOTÓN ---

def calcular():
    id_input = entry_id.get().strip()
    if not id_input:
        messagebox.showwarning("Atención", "Ingresa un ID")
        return

    id_norm = normalizar_id(id_input)
    
    # Buscamos en ambas fuentes
    prod_auto = buscar_producto(id_norm)
    consumo_sabo, stock_sabo = obtener_datos_sabo(id_norm)

    if prod_auto is None and consumo_sabo == 0:
        resultado.set("❌ Producto no encontrado.")
        return

    # Stock Autopiezas (físico - reservado)
    st_auto = 0
    nombre = "Producto Sabo"
    if prod_auto is not None:
        st_auto = float(prod_auto.get("stock_fis", 0)) - float(prod_auto.get("stock_res", 0))
        nombre = prod_auto.get("linea", "Sin descripción")

    # STOCK TOTAL CONSOLIDADO
    stock_total = st_auto + stock_sabo

    # FÓRMULA: If 2 * consumo < stock -> 0, else (2 * consumo) - stock
    if (2 * consumo_sabo) < stock_total:
        pedido = 0
    else:
        pedido = max(0, (2 * consumo_sabo) - stock_total)

    # Actualizar pantalla
    resultado.set(
        f"ID: {id_norm}\n"
        f"Producto: {nombre}\n"
        f"----------------------------------\n"
        f"Stock Total: {stock_total:.0f} (Auto: {st_auto:.0f} + Sabo: {stock_sabo:.0f})\n"
        f"Consumo: {consumo_sabo:.0f}\n"
        f"----------------------------------\n"
        f"CANTIDAD A PEDIR: {pedido:.0f}"
    )

# --- 4. INTERFAZ GRÁFICA ---

ventana = tk.Tk()
ventana.title("Control de Stock - Autopiezas")
ventana.geometry("450x400")

tk.Label(ventana, text="Ingrese ID del Producto:", font=("Arial", 11, "bold")).pack(pady=15)
entry_id = tk.Entry(ventana, font=("Arial", 12), justify="center", width=25)
entry_id.pack()
entry_id.bind('<Return>', lambda e: calcular()) # Calcular al tocar Enter

tk.Button(ventana, text="Calcular Reposición", command=calcular, bg="#2E5077", fg="white", font=("Arial", 10, "bold"), padx=10, pady=5).pack(pady=20)

resultado = tk.StringVar()
resultado.set("Esperando datos...")
lbl_res = tk.Label(ventana, textvariable=resultado, font=("Consolas", 10), justify="left", bg="#F0F0F0", relief="sunken", padx=10, pady=10, width=50)
lbl_res.pack(pady=10)

ventana.mainloop()