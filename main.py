from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config.conexionDB import app
from routes.categoria import router as categoria_router
from routes.proveedor import router as proveedor_router
from routes.producto import router as producto_router
from routes.cliente import router as cliente_router
from routes.venta import router as venta_router
from routes.detalle_venta import router as detalle_venta_router

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(categoria_router,     prefix="/categoria")
app.include_router(proveedor_router,     prefix="/proveedor")
app.include_router(producto_router,      prefix="/producto")
app.include_router(cliente_router,       prefix="/cliente")
app.include_router(venta_router,         prefix="/venta")
app.include_router(detalle_venta_router, prefix="/detalle-venta")

__all__ = ["app"]
