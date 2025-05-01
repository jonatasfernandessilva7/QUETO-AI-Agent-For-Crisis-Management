import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

from src.IA.memoria import (
    obter_estado_memoria,
)
async def obter_estado():
    return obter_estado_memoria()