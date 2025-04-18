from fastapi import FastAPI, UploadFile, File, Request
import datetime
import tempfile
import shutil
import os
from dotenv import load_dotenv
from scipy.io import wavfile

from modelos import Evento
from analise_som import analisar_som_fourier, filtro_passa_baixa, detectar_padroes, salvar_espectrograma
from memoria import (
    adicionar_evento_historico,
    comparar_com_eventos_passados,
    obter_estado_memoria,
    clusterizar_eventos,
    obter_historico_eventos
)
from resposta import resposta_reativa, planejamento_deliberativo
from aprendizado import classificar_evento
from relatorios import gerar_relatorio_llama_local, salvar_relatorio
from email_utils import enviar_email_relatorio

load_dotenv()

app = FastAPI(title="Agente Queto - Gestão de Crises")

@app.post("/evento")
async def receber_evento(evento: Evento):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    adicionar_evento_historico({"evento": evento.dict(), "timestamp": timestamp})

    resposta = resposta_reativa(evento)
    plano = planejamento_deliberativo(evento)
    prioridade = classificar_evento(evento)

    similaridade_msg, evento_similar = comparar_com_eventos_passados(evento)

    relatorio = gerar_relatorio_llama_local(evento, resposta, plano, prioridade)
    arquivo = salvar_relatorio(relatorio, timestamp)
    enviar_email_relatorio(arquivo, os.getenv("EMAIL_DESTINO"))

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
async def receber_audio(file: UploadFile = File(...)):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp:
        shutil.copyfileobj(file.file, temp)
        caminho_temp = temp.name

    try:
        rate, signal = wavfile.read(caminho_temp)
        if signal.ndim > 1:
            signal = signal.mean(axis=1)

        # Análise de Fourier
        analise_fourier = analisar_som_fourier(file)

        signal_filtrado = filtro_passa_baixa(signal, rate)
        espectrograma_path = salvar_espectrograma(signal_filtrado, rate, timestamp)
        padrao = detectar_padroes(signal_filtrado, rate)

        detalhes_evento = {"padrao_detectado": padrao, "arquivo_audio": file.filename}
        # Adicionando os resultados da análise de Fourier aos detalhes do evento
        detalhes_evento.update(analise_fourier)

        evento = Evento(
            tipo="evento_audio",
            origem="sensor_audio",
            detalhes=detalhes_evento
        )

        adicionar_evento_historico({"evento": evento.dict(), "timestamp": timestamp})

        resposta = resposta_reativa(evento)
        plano = planejamento_deliberativo(evento)
        prioridade = classificar_evento(evento)
        similaridade_msg, evento_similar = comparar_com_eventos_passados(evento)

        relatorio = gerar_relatorio_llama_local(evento, resposta, plano, prioridade)
        arquivo_txt = salvar_relatorio(relatorio, timestamp)
        enviar_email_relatorio(arquivo_txt, os.getenv("EMAIL_DESTINO"))

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
        # Adicionando os resultados da análise de Fourier ao retorno
        retorno.update(analise_fourier)
        return retorno
    finally:
        os.remove(caminho_temp)

@app.get("/eventos-clusterizados")
async def eventos_clusterizados(k: int = 3):
    historico = obter_historico_eventos()
    return clusterizar_eventos(historico, k)

@app.get("/estado")
async def obter_estado():
    return obter_estado_memoria()