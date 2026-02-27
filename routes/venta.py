
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.conexionDB import get_conexion

router = APIRouter()

from typing import List

class DetalleVentaInput(BaseModel):
    id_producto: int
    cantidad: int
    precio_unitario: float
    descuento: float
    subtotal: float

class Venta(BaseModel):
    id_cliente: int
    fecha_venta: str        # formato: YYYY-MM-DD
    total: float
    descuento: float
    estado: str             # 'pendiente', 'completada', 'anulada'
    observacion: Optional[str] = None
    items: List[DetalleVentaInput] = []

class VentaUpdate(BaseModel):
    id_cliente: Optional[int] = None
    fecha_venta: Optional[str] = None
    total: Optional[float] = None
    descuento: Optional[float] = None
    estado: Optional[str] = None
    observacion: Optional[str] = None

@router.get("/")
async def listar_ventas(conn = Depends(get_conexion)):
    consulta = """
        SELECT v.id_venta, v.id_cliente,
               c.nombre || ' ' || c.paterno AS cliente,
               v.fecha_venta, v.total, v.descuento, v.estado, v.observacion
        FROM venta v
        JOIN cliente c ON v.id_cliente = c.id_cliente
        ORDER BY v.fecha_venta DESC
    """
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de ventas: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al listar ventas. Consulte con su Administrador")

@router.get("/{id_venta}")
async def obtener_venta(id_venta: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id_venta, id_cliente, fecha_venta, total, descuento, estado, observacion FROM venta WHERE id_venta = %s",
                (id_venta,)
            )
            resultado = await cursor.fetchone()
            if not resultado:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            return resultado
    except Exception as e:
        print(f"Error al obtener venta: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener la venta")

@router.post("/")
async def crear_venta(venta: Venta, conn = Depends(get_conexion)):
    consulta_venta = "INSERT INTO venta(id_cliente, fecha_venta, total, descuento, estado, observacion) VALUES(%s, %s, %s, %s, %s, %s) RETURNING id_venta"
    consulta_detalle = "INSERT INTO detalle_venta(id_venta, id_producto, cantidad, precio_unitario, descuento, subtotal) VALUES(%s, %s, %s, %s, %s, %s)"
    consulta_stock = "UPDATE producto SET stock = stock - %s WHERE id_producto = %s"
    
    try:
        async with conn.cursor() as cursor:
            # 1. Insertar Cabecera de Venta
            await cursor.execute(consulta_venta, (venta.id_cliente, venta.fecha_venta, venta.total, venta.descuento, venta.estado, venta.observacion))
            id_venta = (await cursor.fetchone())['id_venta']
            
            # 2. Insertar Detalles y Actualizar Stock
            for item in venta.items:
                await cursor.execute(consulta_detalle, (id_venta, item.id_producto, item.cantidad, item.precio_unitario, item.descuento, item.subtotal))
                await cursor.execute(consulta_stock, (item.cantidad, item.id_producto))
            
            await conn.commit()
            return {"mensaje": "Venta y detalles registrados exitosamente", "id_venta": id_venta}
    except Exception as e:
        await conn.rollback()
        print(f"Error al registrar venta completa: {e}")
        raise HTTPException(status_code=400, detail=f"No se pudo registrar la venta: {e}")

@router.put("/{id_venta}")
async def actualizar_venta(id_venta: int, venta: Venta, conn = Depends(get_conexion)):
    consulta = """
        UPDATE venta
        SET id_cliente=%s, fecha_venta=%s, total=%s, descuento=%s, estado=%s, observacion=%s
        WHERE id_venta = %s
    """
    parametros = (venta.id_cliente, venta.fecha_venta, venta.total, venta.descuento, venta.estado, venta.observacion, id_venta)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            await conn.commit()
            return {"mensaje": "Venta actualizada exitosamente"}
    except Exception as e:
        print(f"Error al actualizar venta: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la venta")

@router.delete("/{id_venta}")
async def eliminar_venta(id_venta: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM venta WHERE id_venta = %s", (id_venta,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Venta no encontrada")
            await conn.commit()
            return {"mensaje": f"Venta {id_venta} eliminada correctamente"}
    except Exception as e:
        print(f"Error al eliminar venta: {e}")
        raise HTTPException(status_code=400, detail="Error al intentar eliminar la venta")
