import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import os

# --- CONFIGURACIÓN ---
ARCHIVO_STOCK = "autopiezas.beta.xlsx"
ARCHIVO_SABO = "sabo.xlsx"

def normalizar_id(valor):
    if pd.isna(valor): return ""
    return str(valor).strip().replace(".0", "").upper()

def cargar_datos():
    try:
        if not os.path.exists(ARCHIVO_STOCK) or not os.path.exists(ARCHIVO_SABO):
            return None, None
        df_a = pd.read_excel(ARCHIVO_STOCK)
        df_a.columns = df_a.columns.str.strip().str.lower()
        df_a["id"] = df_a["id"].apply(normalizar_id)

        df_s = pd.read_excel(ARCHIVO_SABO)
        df_s.columns = df_s.columns.str.strip()
        df_s.rename(columns={"N° SABO": "id", "Consumo": "cantidad", "stock": "stock_sabo"}, inplace=True)
        df_s["id"] = df_s["id"].apply(normalizar_id)
        return df_a, df_s
    except:
        return None, None

df_stock, df_consumo = cargar_datos()

# --- LÓGICA DE PROCESAMIENTO ---

def generar_y_mostrar_tabla():
    if df_stock is None or df_consumo is None:
        messagebox.showerror("Error", "No se pudieron cargar los archivos Excel.")
        return

    # 1. Procesar datos
    df_res = pd.merge(df_consumo, df_stock[['id', 'stock_fis', 'stock_res', 'linea']], on='id', how='left')
    
    # Limpiar nulos y convertir tipos
    for col in ['stock_fis', 'stock_res', 'cantidad', 'stock_sabo']:
        df_res[col] = pd.to_numeric(df_res[col], errors='coerce').fillna(0)

    df_res['st_auto'] = df_res['stock_fis'] - df_res['stock_res']
    df_res['stock_total'] = df_res['st_auto'] + df_res['stock_sabo']
    
    # Aplicar tu fórmula
    df_res['pedido'] = df_res.apply(lambda r: max(0, (2 * r['cantidad']) - r['stock_total']) if (2 * r['cantidad']) >= r['stock_total'] else 0, axis=1)

    # 2. Limpiar tabla actual en la interfaz
    for item in tabla.get_children():
        tabla.delete(item)

    # 3. Insertar datos en la tabla visual
    for _, fila in df_res.iterrows():
        tabla.insert("", "end", values=(
            fila['id'], 
            fila['linea'] if pd.notna(fila['linea']) else "S/D", 
            int(fila['stock_total']), 
            int(fila['cantidad']), 
            int(fila['pedido'])
        ))
    
    # 4. Guardar Excel (opcional, como respaldo)
    try:
        df_res[['id', 'linea', 'stock_total', 'cantidad', 'pedido']].to_excel("Resultado_Inventario.xlsx", index=False)
    except:
        pass

# --- INTERFAZ GRÁFICA MEJORADA ---

ventana = tk.Tk()
ventana.title("Control de Stock Consolidado")
ventana.geometry("800x600") # Ventana más grande para la tabla

# Panel Superior (Botones)
frame_superior = tk.Frame(ventana)
frame_superior.pack(pady=20)

btn_procesar = tk.Button(
    frame_superior, 
    text="VER TODA LA TABLA Y CALCULAR", 
    command=generar_y_mostrar_tabla, 
    bg="#2E5077", fg="white", 
    font=("Arial", 12, "bold"), 
    padx=20, pady=10
)
btn_procesar.pack()

# Panel de Tabla (Treeview)
frame_tabla = tk.Frame(ventana)
frame_tabla.pack(expand=True, fill="both", padx=20, pady=10)

# Columnas de la tabla
columnas = ("id", "linea", "stock", "consumo", "pedido")
tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")

# Definir encabezados
tabla.heading("id", text="ID / N° SABO")
tabla.heading("linea", text="Descripción / Línea")
tabla.heading("stock", text="Stock Total")
tabla.heading("consumo", text="Consumo")
tabla.heading("pedido", text="A PEDIR")

# Ajustar ancho de columnas
tabla.column("id", width=100, anchor="center")
tabla.column("linea", width=250)
tabla.column("stock", width=100, anchor="center")
tabla.column("consumo", width=100, anchor="center")
tabla.column("pedido", width=100, anchor="center")

# Barra de desplazamiento
scrollbar = ttk.Scrollbar(frame_tabla, orient="vertical", command=tabla.yview)
tabla.configure(yscrollcommand=scrollbar.set)

tabla.pack(side="left", expand=True, fill="both")
scrollbar.pack(side="right", fill="y")

ventana.mainloop()
