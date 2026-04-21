# 🌱 Inventario y Registro de Ventas — Semillas VC

> Sistema de gestión de inventario y punto de venta desarrollado con **Python**, **FastAPI** y **SQLite**, enfocado en resolver necesidades reales de negocio con una interfaz moderna y flujo optimizado.

---

## 📸 Capturas
### Ventas View
> <img width="2007" height="741" alt="image" src="https://github.com/user-attachments/assets/f64ce85c-6428-4293-93d6-ce4faaedc73a" />
### Productos View
> <img width="1994" height="749" alt="image" src="https://github.com/user-attachments/assets/71f4176b-dbe2-4309-a120-92c2ddbadc01" />
### Historial de Venta
> <img width="1986" height="1441" alt="image" src="https://github.com/user-attachments/assets/ede0b824-921f-4f6c-bc3d-690addec150b" />
### Registro de venta
> <img width="1998" height="889" alt="image" src="https://github.com/user-attachments/assets/8aef3f73-a2b4-4592-b1d7-ea755975f73a" />
### Registro de Nuevo Producto
> <img width="2023" height="786" alt="image" src="https://github.com/user-attachments/assets/73dbf1a8-e20d-4e55-8710-61f4736505c7" />
### Filtro de producto por Nombre
> <img width="2036" height="511" alt="image" src="https://github.com/user-attachments/assets/52a836c5-03a9-4f93-9373-06a919ee563b" />
### Filtro de venta realizada por ID
> <img width="2006" height="709" alt="image" src="https://github.com/user-attachments/assets/1e0536bc-5914-4f17-88f7-0ff3707ecb62" />


---

## ✨ Funcionalidades

### 🛒 Punto de Venta
- Selección de múltiples productos en una sola venta
- Cálculo automático del total
- Validación de stock en tiempo real

### 📦 Gestión de Productos
- Alta, edición y eliminación de productos
- Sistema de **activación/desactivación** sin perder historial
- Control de stock automático

### 📋 Historial de Ventas
- Visualización agrupada por venta (tipo ticket)
- Persistencia de nombre y precio al momento de la venta
- Estado de venta (`completada` / `cancelada`)
- Restauración automática de stock al cancelar

### 🎨 Interfaz de Usuario
- UI moderna basada en **Bootstrap + CSS personalizado**
- Paleta de colores profesional (branding tipo negocio real)
- Alertas tipo “toast” (no rompen el layout)
- Animaciones suaves y experiencia fluida

### ⚡ Mejoras Técnicas
- Migraciones automáticas en SQLite (`PRAGMA table_info`)
- Manejo de transacciones (`COMMIT / ROLLBACK`)
- Separación clara entre lógica de negocio y vistas
- Sistema preparado para escalar a API REST

---

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python, FastAPI |
| Base de datos | SQLite3 |
| Frontend | Jinja2 + Bootstrap 5 |
| Estilos | CSS personalizado |
| Servidor | Uvicorn |
| Control de versiones | Git + GitHub |

---

## 🚀 Instalación local

### 1. Clona el repositorio
```bash
git clone https://github.com/arathsam/Inventario-y-Registro-de-Ventas.git
cd Inventario-y-Registro-de-Ventas
```

### 2. Crea y activa el entorno virtual
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. Instala las dependencias
```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### 4. Corre el servidor
```bash
uvicorn main:app --reload
```

### 5. Abre en el navegador
```
http://127.0.0.1:8000
```

---

## 📁 Estructura del proyecto

```
├── main.py                  # Lógica del servidor y rutas
├── inventario.db            # Base de datos SQLite (se crea automáticamente)
├── templates/
│   ├── base.html            # Plantilla base con navbar
│   ├── index.html           # Vista de ventas (página principal)
│   ├── productos.html       # Gestión del catálogo
│   └── ventas.html          # Historial de ventas agrupado
└── static/
    └── css/
        └── styles.css       # Estilos personalizados
```

---

## 🧠 Decisiones Técnicas

- Soft delete (`activo` / `inactivo`) en lugar de eliminar productos
- Persistencia de datos históricos en `venta_items`
- Uso de transacciones (`COMMIT / ROLLBACK`) para evitar inconsistencias en ventas
- Separación de entidades:
  - `productos`
  - `ventas`
  - `venta_items`

> Esta estructura simula la arquitectura de sistemas reales de punto de venta.

---

## 🗺️ Roadmap

- [x] Sistema de ventas con múltiples productos
- [x] Historial agrupado tipo ticket
- [x] Control de stock automático
- [x] UI personalizada con CSS profesional
- [x] Sistema de cancelación de ventas
- [ ] Autenticación de usuarios (login)
- [ ] API REST documentada (Swagger)
- [ ] Dashboard con métricas (ventas, ingresos)
- [ ] Deploy en la nube (Render / Railway / AWS)

---

## 👨‍💻 Autor

Desarrollado por **Arath Samir Mu Yee**  
Para **Mancy Biliana / Semillas VC**
