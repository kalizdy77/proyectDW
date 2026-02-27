
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.conexionDB import get_conexion

router = APIRouter()

class DetalleVenta(BaseModel):
    id_venta: int
    id_producto: int
    cantidad: int
    precio_unitario: float
    descuento: float
    subtotal: float

class DetalleVentaUpdate(BaseModel):
    id_venta: Optional[int] = None
    id_producto: Optional[int] = None
    cantidad: Optional[int] = None
    precio_unitario: Optional[float] = None
    descuento: Optional[float] = None
    subtotal: Optional[float] = None

@router.get("/")
async def listar_detalles(conn = Depends(get_conexion)):
    consulta = """
        SELECT d.id_detalle, d.id_venta, d.id_producto, p.descripcion AS producto,
               d.cantidad, d.precio_unitario, d.descuento, d.subtotal
        FROM detalle_venta d
        JOIN producto p ON d.id_producto = p.id_producto
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de detalles: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al listar detalles. Consulte con su Administrador")

@router.get("/por-venta/{id_venta}")
async def detalles_por_venta(id_venta: int, conn = Depends(get_conexion)):
    """Retorna todos los detalles de una venta específica"""
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                SELECT d.id_detalle, d.id_producto, p.descripcion AS producto,
                       d.cantidad, d.precio_unitario, d.descuento, d.subtotal
                FROM detalle_venta d
                JOIN producto p ON d.id_producto = p.id_producto
                WHERE d.id_venta = %s
                """,
                (id_venta,)
            )
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener detalles de venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener los detalles de la venta")

@router.get("/{id_detalle}")
async def obtener_detalle(id_detalle: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id_detalle, id_venta, id_producto, cantidad, precio_unitario, descuento, subtotal FROM detalle_venta WHERE id_detalle = %s",
                (id_detalle,)
            )
            resultado = await cursor.fetchone()
            if not resultado:
                raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
            return resultado
    except Exception as e:
        print(f"Error al obtener detalle: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener el detalle")

@router.post("/")
async def crear_detalle(detalle: DetalleVenta, conn = Depends(get_conexion)):
    """Agrega un detalle a una venta y descuenta el stock del producto automáticamente"""
    consulta_insert = "INSERT INTO detalle_venta(id_venta, id_producto, cantidad, precio_unitario, descuento, subtotal) VALUES(%s, %s, %s, %s, %s, %s)"
    consulta_stock = "UPDATE producto SET stock = stock - %s WHERE id_producto = %s"
    parametros = (detalle.id_venta, detalle.id_producto, detalle.cantidad, detalle.precio_unitario, detalle.descuento, detalle.subtotal)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta_insert, parametros)
            await cursor.execute(consulta_stock, (detalle.cantidad, detalle.id_producto))
            await conn.commit()
            return {"mensaje": "Detalle de venta registrado y stock actualizado exitosamente"}
    except Exception as e:
        print(f"Error al registrar detalle: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar el detalle. Consulte con su Administrador")

@router.put("/{id_detalle}")
async def actualizar_detalle(id_detalle: int, detalle: DetalleVenta, conn = Depends(get_conexion)):
    consulta = """
        UPDATE detalle_venta
        SET id_venta=%s, id_producto=%s, cantidad=%s, precio_unitario=%s, descuento=%s, subtotal=%s
        WHERE id_detalle = %s
    """
    parametros = (detalle.id_venta, detalle.id_producto, detalle.cantidad, detalle.precio_unitario, detalle.descuento, detalle.subtotal, id_detalle)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
            await conn.commit()
            return {"mensaje": "Detalle de venta actualizado exitosamente"}
    except Exception as e:
        print(f"Error al actualizar detalle: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar el detalle")

@router.delete("/{id_detalle}")
async def eliminar_detalle(id_detalle: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM detalle_venta WHERE id_detalle = %s", (id_detalle,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Detalle de venta no encontrado")
            await conn.commit()
            return {"mensaje": f"Detalle {id_detalle} eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar detalle: {e}")
        raise HTTPException(status_code=400, detail="Error al intentar eliminar el detalle")
