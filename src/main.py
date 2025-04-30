from fastapi import FastAPI
import datetime
import tempfile
import shutil
import os

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
from scipy.io import wavfile

from modelos import Evento
from src.services.service_analise_som import analisar_som_fourier, filtro_passa_baixa, detectar_padroes, salvar_espectrograma
from memoria import (
    adicionar_evento_historico,
    comparar_com_eventos_passados,
    obter_estado_memoria,
    clusterizar_eventos,
    obter_historico_eventos
)
from src.services.service_microfone import gravar_audio_microfone, reconhecer_fala
from src.services.service_resposta import resposta_reativa, planejamento_deliberativo
from aprendizado import classificar_evento
from src.services.service_relatorios import gerar_relatorio_llama_local, salvar_relatorio
from src.services.service_email_utils import enviar_email_com_anexos, enviar_email_relatorio

load_dotenv()

app = FastAPI(title="Agente Queto - Gestão de Crises")

@app.post("/evento")
async def receber_evento(evento: Evento):
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

@app.post("/audio_evento")
async def receber_audio():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    caminho_temp = gravar_audio_microfone(duracao=10)
    
    try:
        rate, signal = wavfile.read(caminho_temp)
        if signal.ndim > 1:
            signal = signal.mean(axis=1)

        # Análise de Fourier
        analise_fourier = analisar_som_fourier(caminho_temp)

        signal_filtrado = filtro_passa_baixa(signal, rate)
        espectrograma_path = salvar_espectrograma(signal_filtrado, rate, timestamp)
        padrao = detectar_padroes(signal_filtrado, rate)

        detalhes_evento = {"padrao_detectado": padrao, "arquivo_audio": caminho_temp}
        detalhes_evento.update(analise_fourier)

        texto_falado = reconhecer_fala(caminho_temp)
        detalhes_evento["texto_falado"] = texto_falado


        tipo_evento_detectado = classificar_evento(detalhes_evento)

        evento = Evento(
            tipo=tipo_evento_detectado,
            origem="microfone_local",
            detalhes=detalhes_evento
        )


        adicionar_evento_historico({"evento": evento.model_dump(), "timestamp": timestamp})

        resposta = resposta_reativa(evento)
        plano = planejamento_deliberativo(evento)
        prioridade = classificar_evento(evento)
        similaridade_msg, evento_similar = comparar_com_eventos_passados(evento)

        relatorio = gerar_relatorio_llama_local(evento, resposta, plano, prioridade)
        arquivo = salvar_relatorio(relatorio, timestamp, prioridade)
        #enviar_email_com_anexos([arquivo, caminho_temp], os.getenv("EMAIL_DESTINO"))

        retorno = {
            "padrao_detectado": padrao,
            "resposta_reativa": resposta,
            "plano_acao": plano,
            "prioridade": prioridade,
            "relatorio": relatorio,
            "similaridade": similaridade_msg,
            "evento_similar": evento_similar,
            "espectrograma": espectrograma_path
        }
        retorno.update(analise_fourier)
        return retorno
    except(TypeError):
        print(TypeError)
    finally:
        os.remove(caminho_temp)


@app.get("/eventos-clusterizados")
async def eventos_clusterizados(k: int = 3):
    historico = obter_historico_eventos()
    return clusterizar_eventos(historico, k)

@app.get("/estado")
async def obter_estado():
    return obter_estado_memoria()