# 🌱 Inventario y Registro de Ventas — Semillas VC

> Sistema de gestión de inventario y punto de venta desarrollado con **Python**, **FastAPI** y **SQLite**, diseñado para el negocio de Semillas VC by Mancy Biliana.

---

## 📸 Capturas

> <img width="2103" height="664" alt="image" src="https://github.com/user-attachments/assets/754c3212-9d01-47ae-87c0-a4e3ffedb139" />
> <img width="2093" height="717" alt="image" src="https://github.com/user-attachments/assets/4e517209-f3d2-44b8-8477-c7be41fec9c8" />
> <img width="2129" height="718" alt="image" src="https://github.com/user-attachments/assets/52f9f30f-edae-4af7-8e66-ba8b21a83666" />
> <img width="2076" height="637" alt="image" src="https://github.com/user-attachments/assets/895bd18d-392a-44d5-80bc-77a1af290472" />
>



---

## ✨ Funcionalidades

- 🛒 **Punto de venta** — selecciona productos, calcula cambio y registra la venta con un clic
- 🔍 **Buscador en tiempo real** — filtra productos mientras escribes
- 📦 **Gestión de catálogo** — agrega, edita y oculta productos sin perder historial
- 📋 **Historial agrupado** — cada venta muestra todos sus productos, precios y total
- 💾 **Historial permanente** — el nombre y precio del producto se guardan al momento de la venta, aunque después se edite o elimine
- ⚡ **Stock automático** — los productos con stock 0 se ocultan del punto de venta automáticamente

---

## 🛠️ Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | [FastAPI](https://fastapi.tiangolo.com/) |
| Base de datos | SQLite3 |
| Frontend | Jinja2 + Bootstrap 5 |
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

## 🗺️ Roadmap

- [x] Sistema de ventas con múltiples productos
- [x] Historial agrupado por sesión de venta
- [x] Buscador en tiempo real
- [x] Ocultar productos sin perder historial
- [ ] Autenticación con login
- [ ] API REST documentada
- [ ] Deploy en la nube

---

## 👩‍💻 Autor

Desarrollado por **Arath Samir** para **Mancy Biliana / Semillas VC**

---

> *Proyecto en desarrollo activo — mejoras continuas* 🚀
