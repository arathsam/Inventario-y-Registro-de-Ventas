# ---------------------------------------- IMPORTACIONES ----------------------------------------
from fastapi import FastAPI
from fastapi import Request
from fastapi import Form
from fastapi import HTTPException
from fastapi import Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import sqlite3
from typing import List, Dict
from fastapi.responses import HTMLResponse


# ---------------------------------------- APP Y PLANTILLAS ----------------------------------------

app = FastAPI(title="Sistema de inventario y venta de MANCY BILIANA")
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# ---------------------------------------- FUNCIONES DE BASE DE DATOS ----------------------------------------

def get_db_connection():
    conn = sqlite3.connect('inventario.db')
    conn.row_factory = sqlite3.Row
    return conn


def init_bd():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL
        )''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )''')
    conn.commit()
    conn.close()


def get_all_products() -> List[Dict]:
    conn = get_db_connection()
    productos = conn.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(producto) for producto in productos]


def create_product(nombre: str, precio: float, stock: int):
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO productos (nombre, precio, stock) VALUES (?,?,?)",
        (nombre, precio, stock)
    )
    conn.commit()
    conn.close()


def update_product(product_id: int, nombre: str, precio: float, stock: int):
    conn = get_db_connection()
    conn.execute(
        "UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
        (nombre, precio, stock, product_id)
    )
    conn.commit()
    conn.close()  # BUG 1 CORREGIDO: era "conn.close" sin paréntesis → no cerraba la conexión


def delete_product(product_id: int):
    conn = get_db_connection()
    conn.execute("DELETE FROM ventas WHERE producto_id = ?", (product_id,))
    # BUG 2 CORREGIDO: era "product_id" → el campo en la tabla se llama "producto_id"
    conn.execute("DELETE FROM productos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()  # BUG 3 CORREGIDO: era "conn.close" sin paréntesis → no cerraba la conexión


def record_multiple_sales(items: List[Dict]) -> tuple:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("BEGIN")
    errores = []
    try:
        for item in items:
            pid = item["producto_id"]
            cant = item["cantidad"]

            if cant <= 0:
                continue

            prod = cursor.execute(
                "SELECT stock, nombre FROM productos WHERE id = ?", (pid,)
            ).fetchone()

            if not prod:
                errores.append(f"Producto ID {pid} no existe")
                continue

            if prod['stock'] < cant:
                errores.append(
                    f"Stock insuficiente para {prod['nombre']} "
                    f"(solicitando: {cant}, disponible: {prod['stock']})"
                )
                continue

            nuevo_stock = prod['stock'] - cant
            cursor.execute(
                "UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, pid)
            )
            cursor.execute(
                "INSERT INTO ventas (producto_id, cantidad) VALUES (?,?)",
                (pid, cant)
            )

        if errores:
            cursor.execute("ROLLBACK")
            conn.close()
            return False, " | ".join(errores)
        else:
            cursor.execute("COMMIT")
            conn.close()
            return True, "Ventas Registradas Correctamente"

    except Exception as e:
        cursor.execute("ROLLBACK")
        conn.close()
        return False, f"Error de Sistema: {str(e)}"


def get_all_sales() -> List[Dict]:
    conn = get_db_connection()
    ventas = conn.execute('''
        SELECT ventas.id, productos.nombre, ventas.cantidad, ventas.fecha
        FROM ventas
        JOIN productos ON ventas.producto_id = productos.id
        ORDER BY ventas.fecha DESC
        ''').fetchall()
    conn.close()
    return [dict(v) for v in ventas]


# ---------------------------------------- RUTAS ----------------------------------------

@app.get("/")
async def home(request: Request, msg: str = None, error: str = None):
    productos = get_all_products()
    # BUG 4 CORREGIDO: apuntaba a "simple.html" (archivo de prueba) en lugar de "index.html"
    return templates.TemplateResponse("index.html", {
        "request": request,
        "productos": productos,
        "msg": msg,
        "error": error
    })


@app.post("/productos")
async def add_product(
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...)
):
    if not nombre or precio <= 0 or stock < 0:
        return RedirectResponse(url="/?error=Datos Invalidos", status_code=303)
    create_product(nombre, precio, stock)
    return RedirectResponse(url="/?msg=Producto Agregado", status_code=303)


@app.post("/productos/{producto_id}/update")
# BUG 5 CORREGIDO: la ruta era "/products/{...}/update" (en inglés) → debe ser "/productos/{...}/update"
async def update_product_route(
    producto_id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...)
):
    update_product(producto_id, nombre, precio, stock)
    return RedirectResponse(url="/?msg=Producto Actualizado", status_code=303)


@app.post("/productos/{producto_id}/delete")
async def remove_producto(producto_id: int):
    delete_product(producto_id)
    return RedirectResponse(url="/?msg=Producto Eliminado", status_code=303)


@app.post("/ventas/multiples")
async def ventas_multiples(request: Request):
    form = await request.form()
    items = []
    for key, value in form.items():
        if key.startswith("cantidad_") and value and int(value) > 0:
            producto_id = int(key.split("_")[1])
            # BUG 6 CORREGIDO: era key.split("_"[1]) → el índice [1] estaba sobre el string "_"
            # no sobre el resultado del split, lo que daba un TypeError silencioso
            cantidad = int(value)
            items.append({"producto_id": producto_id, "cantidad": cantidad})

    if not items:
        return RedirectResponse(url="/?error=No seleccionaste ningun producto", status_code=303)

    exito, mensaje = record_multiple_sales(items)

    if exito:
        return RedirectResponse(url=f"/?msg={mensaje}", status_code=303)
    else:
        return RedirectResponse(url=f"/?error={mensaje}", status_code=303)


@app.get("/ventas/listado")
async def listar_ventas(request: Request):
    ventas = get_all_sales()
    return templates.TemplateResponse("ventas.html", {
        "request": request,
        "ventas": ventas
    })


# ---------------------------------------- INICIALIZAR BD ----------------------------------------
init_bd()