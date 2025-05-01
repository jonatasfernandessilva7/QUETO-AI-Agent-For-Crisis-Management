from fastapi import APIRouter
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

from src.backend.controllers import (
    controller_estado,
    controller_audio,
    controller_cluster,
    controller_evento_texto
)

from src.IA.modelos import Evento

router = APIRouter(
    prefix="/v1"
)

@router.post("/evento-texto")
async def receber_evento(evento: Evento):
    return await controller_evento_texto.receber_evento(evento)

@router.post("/evento-audio")
async def receber_audio():
    return await controller_audio.receber_audio()


@router.get("/eventos-clusterizados")
async def eventos_clusterizados(k: int):
    return await controller_cluster.eventos_clusterizados(k)

@router.get("/estado-memoria")
async def obter_estado():
    return await controller_estado.obter_estado()