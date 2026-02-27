
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.conexionDB import get_conexion

router = APIRouter()

class Cliente(BaseModel):
    ci: str
    nombre: str
    paterno: str
    materno: str
    telefono: str
    email: str
    direccion: str
    activo: bool

class ClienteUpdate(BaseModel):
    ci: Optional[str] = None
    nombre: Optional[str] = None
    paterno: Optional[str] = None
    materno: Optional[str] = None
    telefono: Optional[str] = None
    email: Optional[str] = None
    direccion: Optional[str] = None
    activo: Optional[bool] = None

@router.get("/")
async def listar_clientes(conn = Depends(get_conexion)):
    consulta = "SELECT id_cliente, ci, nombre, paterno, materno, telefono, email, direccion, activo FROM cliente"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de clientes: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al listar clientes. Consulte con su Administrador")

@router.get("/{id_cliente}")
async def obtener_cliente(id_cliente: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id_cliente, ci, nombre, paterno, materno, telefono, email, direccion, activo FROM cliente WHERE id_cliente = %s",
                (id_cliente,)
            )
            resultado = await cursor.fetchone()
            if not resultado:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
            return resultado
    except Exception as e:
        print(f"Error al obtener cliente: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener el cliente")

@router.post("/")
async def crear_cliente(cliente: Cliente, conn = Depends(get_conexion)):
    print(f"Ingresando al cliente")
    consulta = "INSERT INTO cliente(ci, nombre, paterno, materno, telefono, email, direccion, activo) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)"
    parametros = (cliente.ci, cliente.nombre, cliente.paterno, cliente.materno, cliente.telefono, cliente.email, cliente.direccion, cliente.activo)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            await conn.commit()
            return {"mensaje": "Cliente registrado exitosamente"}
    except Exception as e:
        print(f"Error al registrar cliente: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar el cliente. Consulte con su Administrador")

@router.put("/{id_cliente}")
async def actualizar_cliente(id_cliente: int, cliente: Cliente, conn = Depends(get_conexion)):
    consulta = """
        UPDATE cliente
        SET ci=%s, nombre=%s, paterno=%s, materno=%s, telefono=%s, email=%s, direccion=%s, activo=%s
        WHERE id_cliente = %s
    """
    parametros = (cliente.ci, cliente.nombre, cliente.paterno, cliente.materno, cliente.telefono, cliente.email, cliente.direccion, cliente.activo, id_cliente)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
            await conn.commit()
            return {"mensaje": "Cliente actualizado exitosamente"}
    except Exception as e:
        print(f"Error al actualizar cliente: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar el cliente")

@router.delete("/{id_cliente}")
async def eliminar_cliente(id_cliente: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM cliente WHERE id_cliente = %s", (id_cliente,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Cliente no encontrado")
            await conn.commit()
            return {"mensaje": f"Cliente {id_cliente} eliminado correctamente"}
    except Exception as e:
        print(f"Error al eliminar cliente: {e}")
        raise HTTPException(status_code=400, detail="Error al intentar eliminar el cliente")
