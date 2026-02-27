
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

from config.conexionDB import get_conexion

router = APIRouter()

class Categoria(BaseModel):
    descripcion: str
    activo: bool

class CategoriaUpdate(BaseModel):
    descripcion: Optional[str] = None
    activo: Optional[bool] = None

@router.get("/")
async def listar_categorias(conn = Depends(get_conexion)):
    consulta = "SELECT id_categoria, descripcion, activo FROM categoria"
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta)
            return await cursor.fetchall()
    except Exception as e:
        print(f"Error listado de categorias: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al listar categorías. Consulte con su Administrador")

@router.get("/{id_categoria}")
async def obtener_categoria(id_categoria: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(
                "SELECT id_categoria, descripcion, activo FROM categoria WHERE id_categoria = %s",
                (id_categoria,)
            )
            resultado = await cursor.fetchone()
            if not resultado:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")
            return resultado
    except Exception as e:
        print(f"Error al obtener categoría: {e}")
        raise HTTPException(status_code=400, detail="Ocurrió un error al obtener la categoría")

@router.post("/")
async def crear_categoria(categoria: Categoria, conn = Depends(get_conexion)):
    consulta = "INSERT INTO categoria(descripcion, activo) VALUES(%s, %s)"
    parametros = (categoria.descripcion, categoria.activo)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            await conn.commit()
            return {"mensaje": "Categoría registrada exitosamente"}
    except Exception as e:
        print(f"Error al registrar categoría: {e}")
        raise HTTPException(status_code=400, detail="No se pudo registrar la categoría. Consulte con su Administrador")

@router.put("/{id_categoria}")
async def actualizar_categoria(id_categoria: int, categoria: Categoria, conn = Depends(get_conexion)):
    consulta = """
        UPDATE categoria
        SET descripcion=%s, activo=%s
        WHERE id_categoria = %s
    """
    parametros = (categoria.descripcion, categoria.activo, id_categoria)
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(consulta, parametros)
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")
            await conn.commit()
            return {"mensaje": "Categoría actualizada exitosamente"}
    except Exception as e:
        print(f"Error al actualizar categoría: {e}")
        raise HTTPException(status_code=400, detail="No se pudo actualizar la categoría")

@router.delete("/{id_categoria}")
async def eliminar_categoria(id_categoria: int, conn = Depends(get_conexion)):
    try:
        async with conn.cursor() as cursor:
            await cursor.execute("DELETE FROM categoria WHERE id_categoria = %s", (id_categoria,))
            if cursor.rowcount == 0:
                raise HTTPException(status_code=404, detail="Categoría no encontrada")
            await conn.commit()
            return {"mensaje": f"Categoría {id_categoria} eliminada correctamente"}
    except Exception as e:
        print(f"Error al eliminar categoría: {e}")
        raise HTTPException(status_code=400, detail="Error al intentar eliminar la categoría")
