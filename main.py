import pandas as pd

df = pd.read_excel("autopiezas.beta.xlsx")

# Limpiar nombres de columnas
df.columns = df.columns.str.strip()

# Asegurar que id sea texto
df["id"] = df["id"].astype(str)

id_producto = input("Ingrese el ID del producto: ")
consumo = float(input("Ingrese el consumo del producto: "))

encontrado = False

for index, row in df.iterrows():
    if row["id"] == id_producto:
        encontrado = True

        stock = row["stock_fis"] - row["stock_res"]

        if stock > 0 and stock >= 2 * consumo:
            pedir = 0
        else:
            pedir = max(0, 2 * consumo - stock)

        print(f"Producto {id_producto}, Pedir: {pedir}")

if not encontrado:
    print("No se encontró ese ID")