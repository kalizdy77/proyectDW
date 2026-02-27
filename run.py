"""
Punto de entrada para ejecutar la aplicación en Windows
Soluciona el problema del event loop de Psycopg en Windows
"""

import asyncio
import sys

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
