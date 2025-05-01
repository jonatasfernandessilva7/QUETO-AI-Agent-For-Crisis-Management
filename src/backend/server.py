from fastapi import FastAPI
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.backend.routes import api 

app = FastAPI(title="Agente Queto - Gestão de Crises")

# Registrar as rotas corretamente
app.include_router(api.router)