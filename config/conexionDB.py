import asyncio
import sys
from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Configurar event loop para Windows
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Configuración de base de datos  ← CAMBIA AQUÍ tus credenciales y nombre de BD
DB_URL = "postgresql://postgres:12345@localhost:5432/bd_inventario"

# Instancia de la app con lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestiona el ciclo de vida del pool de conexiones"""
    app.async_pool = AsyncConnectionPool(conninfo=DB_URL, open=False)
    try:
        await app.async_pool.open()
        print("✅ Pool de conexiones abierto exitosamente")
        yield
    finally:
        await app.async_pool.close()
        print("🛑 Pool de conexiones cerrado")

app = FastAPI(
    title="API - Sistema de Inventario y Ventas",
    description="API REST para gestión de inventario, ventas, clientes y proveedores",
    version="1.0.0",
    lifespan=lifespan
)

# Dependencia para inyectar la conexión en las rutas
async def get_conexion():
    """Dependency para obtener una conexión del pool"""
    async with app.async_pool.connection() as conn:
        conn.row_factory = dict_row
        yield conn
