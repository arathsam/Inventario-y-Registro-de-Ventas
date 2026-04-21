# ---------------------------------------- IMPORTACIONES ----------------------------------------
from fastapi import FastAPI #importa la clase principal para crear la app web
from fastapi import Request #Permite acceder a datos de la peticion
from fastapi import Form  #Permite recibir datos enviados desde un form html
from fastapi.templating import Jinja2Templates #Cerebro para procesar html dinamico (Frontend)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse #Permite redireccionar despues de una accion
import sqlite3 #Libreria para trabajar SQLite
from typing import List, Dict #Tipado de datos, recibir listas y diccionarios.


# ---------------------------------------- APP Y PLANTILLAS ----------------------------------------

app = FastAPI(title="Sistema de inventario y venta de MANCY BILIANA") #Cre la app FasAPI con el Titulo
templates = Jinja2Templates(directory="templates") #Definimos la carpeta de los archivos HTML
app.mount("/static", StaticFiles(directory="static"), name="static") #Expone la carpeta 'static' en la URL para que el navegador cargue css


# ---------------------------------------- FUNCIONES DE BASE DE DATOS ----------------------------------------

def get_db_connection():
    conn = sqlite3.connect('inventario.db') #Creamos la conexion a la BD SQLite
    conn.row_factory = sqlite3.Row #Permite acceder a las columnas por nombre, en vez de orden numerico.
    return conn #Retorna la conexion


def init_bd(): 
    #Incializa la BD creando las tablas si no existen.
    #Asi mismo realizamos migracion de datos ya existentes a nuevas tablas.
    conn = get_db_connection()
    cursor = conn.cursor()
    
    #TABLA: productos
    #Guardamos todos los productos que querramos registrar.
    #Productos disponibles, columna 'activo' para ocultar productos sin eliminarlos.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS productos(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            stock INTEGER NOT NULL,
            activo INTEGER NOT NULL DEFAULT 1
        )''')
    
    #TABLA: ventas
    #Cada fila representa una venta ('Ticket'). 'Total' suma del precio de todos los productos de esa venta.
    #'estado' Para poder cancelar la venta.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            total REAL NOT NULL DEFAULT 0,
            estado TEXT NOT NULL DEFAULT 'completada'
        )''')
    
    #TABLA: venta_items
    #Cada fila es un producto vendido que corresponde a una venta especifica.
    #Usamos de FK 'venta_id:' -> ventas.id: para saber a que venta pertence
    #Usamos de FK 'producto_id' -> producto.id: para saber que producto fue
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS venta_items(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER NOT NULL,
            producto_id INTEGER,
            nombre_producto TEXT NOT NULL,
            precio_unitario REAL NOT NULL,
            cantidad INTEGER NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (venta_id) REFERENCES ventas (id),
            FOREIGN KEY (producto_id) REFERENCES productos (id)
        )
    ''')

    #MIGRACIONES: agregar columnas nuevas a tablas que ya existen.
    #Si ya existia informacion previa a la implementacion de registro de ventas, entonces se sobre escribne los datos en las tablas nuevas.
    #"PRAGMA table_info()" devuelve la lista de columnas de una tabla
    #
    
    #Leemos las columnas actuales de la tabla 'productos'
    cols_productos = [
        #'fetchall' Devuelve todas las filas de una consulta SQL como un Array de arrays (lista)
        row[1] for row in cursor.execute("PRAGMA table_info(productos)").fetchall() 
    ]

    #Si no existe alguna columna se agrega. En este caso especifico la columna 'activo' 
    if 'activo' not in cols_productos:
        cursor.execute("ALTER TABLE productos ADD COLUMN activo INTEGER NOT NULL DEFAULT 1")

    
    #Guardamos y cerramos conexion
    conn.commit()
    conn.close()


def get_all_products() -> List[Dict]:
    #Obtenemos todos los prodcutos de la tabla producto. Primero activos y luego ocultos.
    #La usamos en el archivo '/productos' donde el admin podra ver todos los productos.

    conn = get_db_connection() #inciamos la conexion
    productos = conn.execute("SELECT * FROM productos ORDER BY nombre ASC, activo DESC").fetchall()
    conn.close()

    return [dict(producto) for producto in productos] #Convertimos la fila sqlite3.Row a dict normal de python.


def get_active_products() -> List[Dict]: 
    #Obtenemos solos los productos con stock mayor a 0 y activos. (activos = 1)
    #La usamos para la vsita principal de venta. Solo lo que se puede vender.

    conn = get_db_connection()
    productos = conn.execute(
        "SELECT * FROM productos WHERE stock > 0 AND activo = 1 ORDER BY nombre ASC"
    ).fetchall()
    
    conn.close()
    return[dict(p) for p in productos] 
    

def create_product(nombre: str, precio: float, stock: int):
    #Inserta un producto nuevo en la tabla 'productos' 
    #Se marca como activo por default
    conn = get_db_connection()
    conn.execute(
        "INSERT INTO productos (nombre, precio, stock, activo) VALUES (?,?,?,1)",
        (nombre, precio, stock)
    )
    conn.commit()
    conn.close()


def update_product(product_id: int, nombre: str, precio: float, stock: int):
    #Actializa el nombre, precio y stock de un producto existente.
    conn = get_db_connection()
    conn.execute(
        "UPDATE productos SET nombre = ?, precio = ?, stock = ? WHERE id = ?",
        (nombre, precio, stock, product_id)
    )
    conn.commit()
    conn.close()  


def toggle_product_activo(product_id: int):
    #Alterna el estado ('Activo/Oculto') de un producto.
    #Si estaba activo (1) lo pone culto (0) // Si estaba oculto (0) lo pone activo (1)
    #Esto nos permite nunca eliminar el producto ni sus registros de venta, Asi los futuros reportes no se rompen.
    conn = get_db_connection()
    conn.execute(
        #CASE WHEN if de SQL
        "UPDATE productos SET activo = CASE WHEN activo = 1 THEN 0 ELSE 1 END WHERE id = ?",(product_id,)
    )
    conn.commit()
    conn.close()


def delete_product(product_id: int):
    #Elimina un producto existente en la BD
    #Tambien elimina sus registros en 'venta_items' para no violar la FK
    #Se usaria en casos muy especificos, despues de obtener reportes/backup de las ventas del producto a eliminar.
    conn = get_db_connection()
    conn.execute("DELETE FROM venta_items WHERE producto_id = ?", (product_id,))
    conn.execute("DELETE FROM productos WHERE id = ?", (product_id,))
    conn.commit()
    conn.close() 


def record_multiple_sales(items: List[Dict]) -> tuple:
    #REGISTRA UNA VENTA CON MULTIPLES PRODUCTOS.
    #Flujo: 
    #1.- Crea un registro en 'ventas' para poder obtener el ticket con estado de completada
    #2.- Por cada producto: Valida el stock, descuenta la cantidad vendida y guarda el prducto vendido en ventas_items
    #3.- Actualza el total en la tabla 'ventas'
    #4.- Si algo falla realiza -> ROLLBACK (Deshace todo)
    #5.- Si todo esta correcto -> COMMIT y se confirman todos los datos.
    #
    #Recibe una lista de dics con 'producto_id' y cantidad
    #Devuelve (True, mensaje) si todo ok | (False, errores) si algo falló

    conn = get_db_connection()
    cursor = conn.cursor()
    
    #BEGIN inicia una transaccion explicita
    #Todos los cambios quedan en espera hasta COMMIT o ROLLBACK
    cursor.execute("BEGIN")
    errores = []
    try:
        #Creamos el registro de la venta (El Ticket)
        #Total en 0 al principio, se actualizaal final de la suma real.
        cursor.execute(
            "INSERT INTO ventas (total, estado) VALUES (0, 'completada')"
        )
        total_venta = 0
        #'lastrowid' -> devuelve el id autogenerado del INSERT anterior
        venta_id = cursor.lastrowid
        
        #Lee con una iteracion los productos selccionados de la lista
        for item in items:
            pid = item["producto_id"]
            cant = item["cantidad"]

            #Si la cantidad es 0 se ignora el item
            if cant <= 0:
                continue

            #Consultamos el producto para obtener el stock, nombre y precio actual
            prod = cursor.execute(
                "SELECT stock, nombre, precio FROM productos WHERE id = ?", (pid,)
            ).fetchone()#Solo regresa la info del producto (la info de la fila seleccionada en la bd)

            #Si el prodcuto no existe en la BD marcamos error y continua con el siguiente
            if not prod:
                errores.append(f"Producto ID {pid} no existe")
                continue

            #Validamos que exista el stock suficiente
            if prod['stock'] < cant:
                errores.append(
                    f"Stock insuficiente para {prod['nombre']} "
                    f"(solicitando: {cant}, disponible: {prod['stock']})"
                )
                continue

            #Calculamos el subtotal del item (precio*cantidad)
            subtotal = prod['precio']*cant

            #Actualizamos el stock del producto restando la cantidad vendida.
            nuevo_stock = prod['stock'] - cant
            cursor.execute(
                "UPDATE productos SET stock = ? WHERE id = ?", (nuevo_stock, pid)
            )

            #Insertamos el item (producto vendido) en la tabla 'venta_items'
            #Guardamos nombre y precio como copia del momento de la venta para tener un historial.
            cursor.execute(
                """
                INSERT INTO venta_items
                (venta_id, producto_id, nombre_producto, precio_unitario, cantidad, subtotal)
                VALUES (?,?,?,?,?,?)""",
                (venta_id, pid, prod['nombre'], prod['precio'], cant, subtotal)
            )

            #Acumulamos al total de la venta
            total_venta += subtotal

        #Si hubo errores, deshacemos todo
        if errores:
            cursor.execute("ROLLBACK")
            conn.close()
            return False, " | ".join(errores)
        
        #Actualizar el total real en el registro de la venta. (En la tabla ventas)
        cursor.execute(
            "UPDATE ventas SET total = ? WHERE id = ?",
            (total_venta, venta_id)
        )

        #COMMIT para confirmar los cambios en la BD
        cursor.execute("COMMIT")
        conn.close()
        return True, f"Venta #{venta_id} registrada correctamente"

    except Exception as e:
        #Error ramdom (perdida de conexion, se fue la luz, etc.) -> Se deshace todo en este caso
        cursor.execute("ROLLBACK")
        conn.close()
        return False, f"Error de Sistema: {str(e)}"


def cancelar_venta(venta_id: int) -> tuple:
    #Cancela alguna venta existente. Ya sea por devolucion de producto o equis caso.
    #Cambia el estado a 'cancelada' && Devuelve el stock de cada producto.

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("BEGIN")

    try:
        #Verificamos que la venta exista y no este cancelada
        venta = cursor.execute(
            "SELECT id, estado FROM ventas WHERE id = ?", (venta_id,)
        ).fetchone()

        if not venta: 
            cursor.execute("ROLLBACK")
            conn.close()
            return False, "La venta no existe"
        
        if venta['estado'] == 'cancelada':
            cursor.execute("ROLLBACK")
            conn.close()
            return False, "La venta ya ha sido cancelada"
        
        #Si si existe, Obtenemos los items de la venta para devolver el stock
        items = cursor.execute(
            "SELECT producto_id, cantidad FROM venta_items WHERE venta_id = ?",
            (venta_id,)
        ).fetchall()

        #Por cada item, devolvemos la cantidad al stock del producto
        for item in items:
            cursor.execute(
                "UPDATE productos SET stock = stock + ? WHERE id = ?",
                (item['cantidad'], item['producto_id'])
            )

        #Marcamos la venta como cancelada. Cambiamos el estado del producto
        cursor.execute(
            "UPDATE ventas SET estado = 'cancelada' WHERE id = ?",
            (venta_id,)
        )

        #Guardamos en la BD
        cursor.execute("COMMIT")
        conn.close()
        return True, f"Venta {venta_id} cancelada. Stock restaurado."
    
    except Exception as e:
        cursor.execute("ROLLBACK")
        conn.close()
        return False, f"Error de sistema: {str(e)}"


def get_all_sales() -> List[Dict]:
    #Obtenemos todas las ventas con sus items. 
    #Devuelve lista de dics con: id, fecha, total, estado y lista de items.
    conn = get_db_connection()

    #Todas las ventas ordenadas por fecha Descendente (Mas reciente primero)
    ventas = conn.execute(
        "SELECT id, fecha, total, estado FROM ventas ORDER BY fecha DESC"
    ).fetchall()

    resultado = []
    for venta in ventas:
        #Por cada venta obtenemos todos los productos desde 'venta_items'
        items = conn.execute(
            '''SELECT nombre_producto, cantidad, precio_unitario, subtotal
               FROM venta_items WHERE venta_id = ?''',
            (venta['id'],)
        ).fetchall()

        resultado.append({
            "id":     venta['id'],
            "fecha":  venta['fecha'],
            "total":  venta['total'],
            "estado": venta['estado'],
            "items":  [dict(i) for i in items]
        })

    conn.close()
    return resultado


# ---------------------------------------- RUTAS ----------------------------------------
#--------VISTA PRINCIPAL - Punto de Venta
#Solo muestra los productos con stock mayor a 0 y activos para vender
@app.get("/")
async def home(request: Request, msg: str = None, error: str = None):
    productos = get_active_products() #
    return templates.TemplateResponse("index.html", {
        "request": request,
        "productos": productos,
        "msg": msg,
        "error": error
    })



#--------VISTA PRODUCTOS - Gestion de Productos.
#Muestra todos los productos incluyendo los ocultos. (o con stock = o)
@app.get("/productos")
async def catalogo(request: Request, msg: str = None, error: str = None):
    productos = get_all_products()
    return templates.TemplateResponse("productos.html", {
        "request": request,
        "productos": productos,
        "msg": msg,
        "error": error
    })



#---------AGREGAR PRODUCTO - POST desde el modal de /productos
@app.post("/productos/nuevo")
async def add_product(
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...)
):
    if not nombre or precio <= 0 or stock < 0:
        return RedirectResponse(url="/productos?error=Datos Invalidos", status_code=303)
    create_product(nombre, precio, stock)
    return RedirectResponse(url="/productos?msg=Producto Agregado", status_code=303)



#---------ACTUALIZAR PRODUCTO - POST desde el modal de edicion
@app.post("/productos/{producto_id}/update")
async def update_product_route(
    producto_id: int,
    nombre: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...)
):
    update_product(producto_id, nombre, precio, stock)
    return RedirectResponse(url="/productos?msg=Producto Actualizado", status_code=303)



#--------TOGGLE ACTIVO - Oculta o muestra un producto sin eliminarlo
@app.post("/productos/{producto_id}/toggle")
async def toggle_producto(producto_id: int):
    toggle_product_activo(producto_id)
    return RedirectResponse(url="/productos?msg=Producto actualizado|cambio de estatus", status_code=303)



#----------ELIMINAR PRODUCTO - Eliminacion de producto en la BD (rompe el historial de ventas)
@app.post("/productos/{producto_id}/delete")
async def remove_producto(producto_id: int):
    delete_product(producto_id)
    return RedirectResponse(url="/productos?msg=Producto Eliminado", status_code=303)



#----------REGISTRAR VENTA - POST desde el modal de la confirmacion
#--Lee los campos 'cantidad_<id>' del formuladio
@app.post("/ventas/multiples")
async def ventas_multiples(request: Request):
    form = await request.form()
    items = []


    for key, value in form.items():
        #Los campos tienen formato "cantidad_<producto_id>"
        if key.startswith("cantidad_") and value and int(value) > 0:
            producto_id = int(key.split("_")[1]) #Extraemos el ID del nombre del campo
            cantidad = int(value)
            items.append({"producto_id": producto_id, "cantidad": cantidad})

    if not items:
        return RedirectResponse(url="/?error=No seleccionaste ningun producto", status_code=303)

    exito, mensaje = record_multiple_sales(items)

    if exito:
        return RedirectResponse(url=f"/?msg={mensaje}", status_code=303)
    else:
        return RedirectResponse(url=f"/?error={mensaje}", status_code=303)



#------------CANCELAR VENTA - POST desde el historial de ventas
@app.post("/ventas/{venta_id}/cancelar")
async def cancelar_venta_route(venta_id: int):
    exito, mensaje = cancelar_venta(venta_id)

    if exito:
        return RedirectResponse(url=f"/ventas/listado?msg={mensaje}", status_code=303)
    else:
        return RedirectResponse(url=f"/ventas/listado?error={mensaje}", status_code=303)



#----------HISTORIAL DE VENTAS - Muestra todas las ventas agrupadas con fltros
@app.get("/ventas/listado")
async def listar_ventas(request: Request, msg: str = None, error: str = None):
    ventas = get_all_sales()
    return templates.TemplateResponse("ventas.html", {
        "request": request,
        "ventas": ventas,
        "msg": msg,
        "error": error
    })


# ---------------------------------------- INICIALIZAR BD ----------------------------------------
init_bd()