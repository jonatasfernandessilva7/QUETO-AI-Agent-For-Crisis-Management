import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..","..")))

from scipy.io import wavfile
from dotenv import load_dotenv
from src.IA.modelos import Evento
from src.backend.services.service_analise_som import analisar_som_fourier, filtro_passa_baixa, detectar_padroes, salvar_espectrograma
from src.IA.memoria import (
    adicionar_evento_historico,
    comparar_com_eventos_passados
)
from src.backend.services.service_microfone import gravar_audio_microfone, reconhecer_fala
from src.IA.services.service_resposta import resposta_reativa, planejamento_deliberativo
from src.IA.aprendizado import classificar_evento
from src.IA.services.service_relatorios import gerar_relatorio_llama_local, salvar_relatorio
from src.backend.services.service_email_utils import enviar_email_com_anexos, enviar_email_relatorio

load_dotenv()

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