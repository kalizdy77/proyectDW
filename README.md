# Sistema de Inventario y Ventas

API RESTful construida con **FastAPI** + **PostgreSQL** (psycopg3 async pool).

## Estructura del proyecto

```
ProyectoDW/
├── config/
│   ├── __init__.py
│   └── conexionDB.py       ← Configurar credenciales aquí
├── routes/
│   ├── __init__.py
│   ├── categoria.py
│   ├── proveedor.py
│   ├── producto.py
│   ├── cliente.py
│   ├── venta.py
│   └── detalle_venta.py
├── main.py
├── run.py
└── pyproject.toml
```

## Requisitos

- Python 3.11+
- PostgreSQL con la base de datos `bd_inventario` creada

## Instalación

```bash
pip install -e .
```

O con uv:
```bash
uv pip install -e .
```

## Configurar la BD

Edita `config/conexionDB.py` y modifica la variable `DB_URL`:
```python
DB_URL = "postgresql://USUARIO:PASSWORD@localhost:5432/bd_inventario"
```

Luego ejecuta el script SQL `bd_inventario.sql` en PostgreSQL para crear las tablas.

## Ejecutar

```bash
python run.py
```

La API estará disponible en: http://localhost:8000

Documentación interactiva: http://localhost:8000/docs

## Endpoints disponibles

| Recurso        | Prefijo          |
|----------------|-----------------|
| Categorías     | `/categorias`   |
| Proveedores    | `/proveedores`  |
| Productos      | `/productos`    |
| Clientes       | `/clientes`     |
| Ventas         | `/ventas`       |
| Detalle Venta  | `/detalle-venta`|
