from numpy import rint
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import os

ARCHIVO_STOCK = "autopiezas.beta.xlsx"
ARCHIVO_SABO = "sabo.xlsx"
ARCHIVO_CLIENTES = "Pendientes_clientes.xlsx"


def normalizar_id(valor):
    if pd.isna(valor):
        return ""
    return str(valor).strip().replace(".0", "").upper()

def cargar_datos():
    try:
        if not all(os.path.exists(a) for a in [
            ARCHIVO_STOCK,
            ARCHIVO_SABO,
            ARCHIVO_CLIENTES
        ]):
            return None, None, None

        # archivo autopiezas
        df_a = pd.read_excel(ARCHIVO_STOCK)
        df_a.columns = df_a.columns.str.strip().str.lower()
        df_a["id"] = df_a["id"].apply(normalizar_id)

        # archivo sabo
        df_s = pd.read_excel(ARCHIVO_SABO)
        df_s.columns = df_s.columns.str.strip()

        df_s.rename(columns={
            "N° SABO": "id",
            "Consumo": "cantidad",
            "stock": "stock_sabo"
        }, inplace=True)

        df_s["id"] = df_s["id"].apply(normalizar_id)

        # pedidos clientes
        df_c = pd.read_excel(ARCHIVO_CLIENTES)
        df_c.columns = df_c.columns.str.strip().str.lower()

        df_c.rename(columns={
            "etiquetas de fila": "id",
            "suma de cantpend": "pc"
        }, inplace=True)

        df_c["id"] = df_c["id"].apply(normalizar_id)
        df_c["pc"] = pd.to_numeric(df_c["pc"], errors="coerce").fillna(0)

        return df_a, df_s, df_c

    except Exception as e:
        print(f"Error al cargar archivos: {e}")
        return None, None, None

#archivo autopiezas
        df_a = pd.read_excel(ARCHIVO_STOCK)
    df_a.columns = df_a.columns.str.strip().str.lower()
    df_a["id"] = df_a["id"].apply(normalizar_id)
#archivo sabo
    df_s = pd.read_excel(ARCHIVO_SABO)
    df_s.columns = df_s.columns.str.strip()
    df_s.rename(columns={
            "N° SABO": "id",
            "Consumo": "cantidad",
            "stock": "stock_sabo"
        }, inplace=True)

    df_s["id"] = df_s["id"].apply(normalizar_id)
#pedidos clientes
    df_c = pd.read_excel(ARCHIVO_CLIENTES)
    df_c.columns = df_c.columns.str.strip().str.lower()
#en teoria los files ya corren biene

    df_c.rename(columns={
            "etiquetas de fila": "id",
            "suma de cantpend": "pc"
        }, inplace=True)

    df_c["id"] = df_c["id"].apply(normalizar_id)
    df_c["pc"] = pd.to_numeric(
            df_c["pc"],
            errors="coerce"
        ).fillna(0)

    return df_a, df_s, df_c
    print(f"Error al cargar archivos: {e}")
    return None, None, None

df_stock, df_consumo, df_clientes = cargar_datos()


def obtener_calculo_producto(id_buscado):
    id_norm = normalizar_id(id_buscado)

#autopiezas
    p_auto = df_stock[df_stock["id"] == id_norm] if df_stock is not None else pd.DataFrame()

    st_auto = 0
    linea = "S/D"

    if not p_auto.empty:
        prod = p_auto.iloc[0]
        st_auto = float(prod.get("stock_fis", 0)) - float(prod.get("stock_res", 0))
        linea = prod.get("linea", "Sin descripción")

#sabo
    reg_sabo = df_consumo[df_consumo["id"] == id_norm] if df_consumo is not None else pd.DataFrame()

    st_sabo = 0
    consumo = 0

    if not reg_sabo.empty:
        st_sabo = pd.to_numeric(
            reg_sabo["stock_sabo"],
            errors="coerce"
        ).fillna(0).sum()

        consumo = pd.to_numeric(
            reg_sabo["cantidad"],
            errors="coerce"
        ).fillna(0).sum()

#nuevo: pendientes de los clientes 
    reg_clientes = df_clientes[
        df_clientes["id"] == id_norm
    ] if df_clientes is not None else pd.DataFrame()

    pc = 0

    if not reg_clientes.empty:
        pc = pd.to_numeric(
            reg_clientes["pc"],
            errors="coerce"
        ).fillna(0).sum()

#actualizavcion de formula en cálculo de pedido
    stock_total = st_auto + st_sabo

    pedido = max(
        0,
        (2 * consumo) - stock_total + pc
    )

    return {
        "id": id_norm,
        "linea": linea,
        "st_auto": st_auto,
        "st_sabo": st_sabo,
        "pc": pc,
        "stock_total": stock_total,
        "consumo": consumo,
        "pedido": pedido
    }
    
def buscar_individual():
    id_input = entry_busqueda.get().strip()

    if not id_input:
        messagebox.showwarning("Atención", "Ingrese un código")
        return

    res = obtener_calculo_producto(id_input)

    if res["consumo"] == 0 and res["stock_total"] == 0 and res["pc"] == 0:
        texto_resultado.set("Producto no encontrado.")
        return

    texto_resultado.set(
        f"ID: {res['id']}\n"
        f"Descripción: {res['linea']}\n"
        f"{'-'*40}\n"
        f"Stock Total: {res['stock_total']:.0f}\n"
        f"Consumo: {res['consumo']:.0f}\n"
        f"Pend. Clientes: {res['pc']:.0f}\n"
        f"{'-'*40}\n"
        f"CANTIDAD A PEDIR: {res['pedido']:.0f}"
    )


def cargar_tabla_completa():
    if df_consumo is None:
        messagebox.showerror("Error", "No se cargaron datos")
        return

    for item in tabla.get_children():
        tabla.delete(item)

    ids = df_consumo["id"].dropna().unique()

    for _id in ids:
        res = obtener_calculo_producto(_id)

        tabla.insert("", "end", values=(
            res["id"],
            res["linea"],
            int(res["stock_total"]),
            int(res["consumo"]),
            int(res["pc"]),
            int(res["pedido"])
        ))

#programa no corre sin interfaz gráfica

#sigue sin funcionar

#codigo pendiente de la interfaz grafica.


ventana = tk.Tk()
ventana.title("Sistema de Gestión de Repuestos")
ventana.geometry("950x700")
ventana.resizable(True, True)

notebook = ttk.Notebook(ventana)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

#tabla 1 de la interfaz grafica
tab1 = ttk.Frame(notebook)
notebook.add(tab1, text="🔍 Buscar por Código")

tk.Label(
    tab1,
    text="Ingrese N° SABO o ID:",
    font=("Arial", 13, "bold")
).pack(pady=20)

entry_busqueda = tk.Entry(
    tab1,
    font=("Arial", 14),
    justify="center",
    width=30
)

#alertas en busqueda individual, solucionar
entry_busqueda.pack(pady=10)
entry_busqueda.bind("<Return>", lambda e: buscar_individual())

tk.Button(
    tab1,
    text="CONSULTAR",
    command=buscar_individual,
    bg="#2E5077",
    fg="white",
    font=("Arial", 11, "bold"),
    padx=25,
    pady=8
).pack(pady=15)

texto_resultado = tk.StringVar(value="Esperando búsqueda...")

lbl_res = tk.Label(
    tab1,
    textvariable=texto_resultado,
    font=("Consolas", 11),
    justify="left",
    anchor="nw",
    bg="#F8F9FA",
    relief="solid",
    bd=1,
    padx=20,
    pady=20,
    width=65,
    height=14
)
lbl_res.pack(pady=20)

tab2 = ttk.Frame(notebook)
notebook.add(tab2, text="📋 Listado Completo")

frame_controles = tk.Frame(tab2)
frame_controles.pack(fill="x", pady=10)

#alertas en carga de tabla completa: solucionar
tk.Button(
    frame_controles,
    text="🔄 CARGAR / ACTUALIZAR TABLA",
    command=cargar_tabla_completa,
    bg="#D4AC0D",
    fg="black",
    font=("Arial", 10, "bold"),
    padx=20,
    pady=8
).pack()

frame_tabla = tk.Frame(tab2)
frame_tabla.pack(expand=True, fill="both", padx=10, pady=10)

#columnas nuevas
cols = ("id", "desc", "stk", "cons", "pc", "ped")

tabla = ttk.Treeview(
    frame_tabla,
    columns=cols,
    show="headings"
)

tabla.heading("id", text="ID")
tabla.heading("desc", text="Descripción")
tabla.heading("stk", text="Stock Total")
tabla.heading("cons", text="Consumo")
tabla.heading("pc", text="Pend. Clientes")
tabla.heading("ped", text="Cantidad a Pedir")
tabla.column("id", width=120, anchor="center")
tabla.column("desc", width=320)
tabla.column("stk", width=110, anchor="center")
tabla.column("cons", width=100, anchor="center")
tabla.column("pc", width=130, anchor="center")
tabla.column("ped", width=140, anchor="center")

scroll_y = ttk.Scrollbar(
    frame_tabla,
    orient="vertical",
    command=tabla.yview
)

scroll_x = ttk.Scrollbar(
    frame_tabla,
    orient="horizontal",
    command=tabla.xview
)

tabla.configure(
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

tabla.pack(side="top", expand=True, fill="both")
scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

ventana.mainloop()


#Buscar formas de exportar aplicaciones a un archivo excel

#error en linea 170: No encuentrwa el commando+buscar_individual, solucionar   
#faggots 

#enteoria esta mal ubicado el la revision de archivos  del excel,supuestamente se mezclan con el back end

#programaa anda muy lento con 10 archvios,