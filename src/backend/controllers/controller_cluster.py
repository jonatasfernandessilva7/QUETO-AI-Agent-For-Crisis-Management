import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

from src.IA.memoria import (
    clusterizar_eventos,
    obter_historico_eventos
)

async def eventos_clusterizados(k: int = 3):
    historico = obter_historico_eventos()
    return clusterizar_eventos(historico, k)
