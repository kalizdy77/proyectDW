
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.conexionDB import get_conexion

router = APIRouter()

class Proveedor(BaseModel):
    nombre: str
    contacto: str
    telefono: str
    email: str
    direccion: str
    activo: bool

class ProveedorUpdate(BaseModel):
    nombre: Optional[str] = None
    contacto: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

@router.get("/")
async def listar_proveedores(conn = Depends(get_conexion)):
    consulta = "SELECT id_proveedor, nombre, contacto, telefono, email, direccion, activo FROM proveedor"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de proveedores: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al listar proveedores. Consulte con su Administrador")

@router.get("/{id_proveedor}")
async def obtener_proveedor(id_proveedor: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id_proveedor, nombre, contacto, telefono, email, direccion, activo FROM proveedor WHERE id_proveedor = %s",
                (id_proveedor,)
            )
            resultado = await cursor.fetchone()
            if not resultado:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
            return resultado
    except Exception as e:
        print(f"Error al obtener proveedor: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener el proveedor")

@router.post("/")
async def crear_proveedor(proveedor: Proveedor, conn = Depends(get_conexion)):
    consulta = "INSERT INTO proveedor(nombre, contacto, telefono, email, direccion, activo) VALUES(%s, %s, %s, %s, %s, %s)"
    parametros = (proveedor.nombre, proveedor.contacto, proveedor.telefono, proveedor.email, proveedor.direccion, proveedor.activo)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            await conn.commit()
            return {"mensaje": "Proveedor registrado exitosamente"}
    except Exception as e:
        print(f"Error al registrar proveedor: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar el proveedor. Consulte con su Administrador")

@router.put("/{id_proveedor}")
async def actualizar_proveedor(id_proveedor: int, proveedor: Proveedor, conn = Depends(get_conexion)):
    consulta = """
        UPDATE proveedor
        SET nombre=%s, contacto=%s, telefono=%s, email=%s, direccion=%s, activo=%s
        WHERE id_proveedor = %s
    """
    parametros = (proveedor.nombre, proveedor.contacto, proveedor.telefono, proveedor.email, proveedor.direccion, proveedor.activo, id_proveedor)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
            await conn.commit()
            return {"mensaje": "Proveedor actualizado exitosamente"}
    except Exception as e:
        print(f"Error al actualizar proveedor: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar el proveedor")

@router.delete("/{id_proveedor}")
async def eliminar_proveedor(id_proveedor: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM proveedor WHERE id_proveedor = %s", (id_proveedor,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Proveedor no encontrado")
            await conn.commit()
            return {"mensaje": f"Proveedor {id_proveedor} eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar proveedor: {e}")
        raise HTTPException(status_code=400, detail="Error al intentar eliminar el proveedor")
