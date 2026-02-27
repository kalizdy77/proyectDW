
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.conexionDB import get_conexion

router = APIRouter()

class Producto(BaseModel):
    id_categoria: int
    id_proveedor: int
    codigo: str
    descripcion: str
    precio_compra: float
    precio_venta: float
    stock: int
    stock_minimo: int
    unidad: str
    activo: bool

class ProductoUpdate(BaseModel):
    id_categoria: Optional[int] = None
    id_proveedor: Optional[int] = None
    codigo: Optional[str] = None
    descripcion: Optional[str] = None
    precio_compra: Optional[float] = None
    precio_venta: Optional[float] = None
    stock: Optional[int] = None
    stock_minimo: Optional[int] = None
    unidad: Optional[str] = None
    activo: Optional[bool] = None

@router.get("/")
async def listar_productos(conn = Depends(get_conexion)):
    consulta = """
        SELECT p.id_producto, p.id_categoria, c.descripcion AS categoria,
               p.id_proveedor, pr.nombre AS proveedor,
               p.codigo, p.descripcion, p.precio_compra, p.precio_venta,
               p.stock, p.stock_minimo, p.unidad, p.activo
        FROM producto p
        JOIN categoria c ON p.id_categoria = c.id_categoria
        JOIN proveedor pr ON p.id_proveedor = pr.id_proveedor
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de productos: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al listar productos. Consulte con su Administrador")

@router.get("/bajo-stock")
async def productos_bajo_stock(conn = Depends(get_conexion)):
    """Retorna productos con stock menor o igual al stock mínimo"""
    consulta = "SELECT id_producto, codigo, descripcion, stock, stock_minimo, unidad FROM producto WHERE stock <= stock_minimo AND activo = true"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener productos bajo stock: {e}")
        raise HTTPException(status_code=400, detail="Error al obtener productos con bajo stock")

@router.get("/{id_producto}")
async def obtener_producto(id_producto: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id_producto, id_categoria, id_proveedor, codigo, descripcion, precio_compra, precio_venta, stock, stock_minimo, unidad, activo FROM producto WHERE id_producto = %s",
                (id_producto,)
            )
            resultado = await cursor.fetchone()
            if not resultado:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            return resultado
    except Exception as e:
        print(f"Error al obtener producto: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener el producto")

@router.post("/")
async def crear_producto(producto: Producto, conn = Depends(get_conexion)):
    consulta = "INSERT INTO producto(id_categoria, id_proveedor, codigo, descripcion, precio_compra, precio_venta, stock, stock_minimo, unidad, activo) VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    parametros = (producto.id_categoria, producto.id_proveedor, producto.codigo, producto.descripcion, producto.precio_compra, producto.precio_venta, producto.stock, producto.stock_minimo, producto.unidad, producto.activo)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            await conn.commit()
            return {"mensaje": "Producto registrado exitosamente"}
    except Exception as e:
        print(f"Error al registrar producto: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar el producto. Consulte con su Administrador")

@router.put("/{id_producto}")
async def actualizar_producto(id_producto: int, producto: Producto, conn = Depends(get_conexion)):
    consulta = """
        UPDATE producto
        SET id_categoria=%s, id_proveedor=%s, codigo=%s, descripcion=%s, precio_compra=%s,
            precio_venta=%s, stock=%s, stock_minimo=%s, unidad=%s, activo=%s
        WHERE id_producto = %s
    """
    parametros = (producto.id_categoria, producto.id_proveedor, producto.codigo, producto.descripcion, producto.precio_compra, producto.precio_venta, producto.stock, producto.stock_minimo, producto.unidad, producto.activo, id_producto)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            await conn.commit()
            return {"mensaje": "Producto actualizado exitosamente"}
    except Exception as e:
        print(f"Error al actualizar producto: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar el producto")

@router.delete("/{id_producto}")
async def eliminar_producto(id_producto: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM producto WHERE id_producto = %s", (id_producto,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Producto no encontrado")
            await conn.commit()
            return {"mensaje": f"Producto {id_producto} eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar producto: {e}")
        raise HTTPException(status_code=400, detail="Error al intentar eliminar el producto")
