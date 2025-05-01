import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

from dotenv import load_dotenv
from fastapi import HTTPException

from src.IA.modelos import Evento
from src.IA.memoria import (
    adicionar_evento_historico,
    comparar_com_eventos_passados,
)
from src.IA.services.service_resposta import resposta_reativa, planejamento_deliberativo
from src.IA.aprendizado import classificar_evento
from src.IA.services.service_relatorios import gerar_relatorio_llama_local, salvar_relatorio
from src.backend.services.service_email_utils import enviar_email_com_anexos, enviar_email_relatorio

load_dotenv()

async def receber_evento(evento: Evento):
    try:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        adicionar_evento_historico({"evento": evento.model_dump(), "timestamp": timestamp})

        resposta = resposta_reativa(evento)
        plano = planejamento_deliberativo(evento)
        prioridade = classificar_evento(evento)

        similaridade_msg, evento_similar = comparar_com_eventos_passados(evento)

        relatorio = gerar_relatorio_llama_local(evento, resposta, plano, prioridade)
        arquivo = salvar_relatorio(relatorio, timestamp, prioridade)
        #enviar_email_relatorio(arquivo, os.getenv("EMAIL_DESTINO"))

        return {
            "resposta_reativa": resposta,
            "plano_acao": plano,
            "prioridade": prioridade,
            "relatorio": relatorio,
            "similaridade": similaridade_msg,
            "evento_similar": evento_similar,
            "timestamp": timestamp
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))