from fastapi import FastAPI, Request, UploadFile, File
from pydantic import BaseModel
from typing import Dict
import datetime
import requests
import os
import smtplib
from email.message import EmailMessage
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
import tempfile
import shutil
from dotenv import load_dotenv
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

app = FastAPI(title="Agente Queto - Gestão de Crises")

# ----------------------------
# MODELO DE DADOS
# ----------------------------
class Evento(BaseModel):
    tipo: str
    origem: str
    detalhes: Dict[str, str]

# ----------------------------
# ANÁLISE DE SOM COM FOURIER
# ----------------------------

def analisar_som_fourier(file: UploadFile):
    try:
        data, samplerate = sf.read(file.file)

        if len(data.shape) > 1:
            data = data[:, 0]

        N = len(data)
        yf = fft(data)
        xf = fftfreq(N, 1 / samplerate)

        idx = np.where(xf > 0)
        frequencias = xf[idx]
        amplitudes = np.abs(yf[idx])

        pico_frequencia = frequencias[np.argmax(amplitudes)]
        pico_amplitude = np.max(amplitudes)

        return {
            "pico_frequencia": float(pico_frequencia),
            "pico_amplitude": float(pico_amplitude),
            "status": "analisado"
        }

    except Exception as e:
        return {"erro": str(e)}

# ----------------------------
# FILTRO DE RUÍDO
# ----------------------------
def filtro_passa_baixa(signal, rate, cutoff=4000):
    nyquist = 0.5 * rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(6, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, signal)

# ----------------------------
# DETECÇÃO SIMPLES DE PADRÕES
# ----------------------------
def detectar_padroes(signal, rate):
    energia = np.sum(signal ** 2)
    if energia > 1e12:
        return "Explosão detectada"
    elif np.mean(np.abs(signal)) > 1000:
        return "Grito ou alarme detectado"
    else:
        return "Ambiente calmo ou desconhecido"

# ----------------------------
# ESPECTROGRAMA
# ----------------------------
def salvar_espectrograma(signal, rate, timestamp):
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"espectrograma_{timestamp}.png")

    plt.figure(figsize=(10, 4))
    plt.specgram(signal, Fs=rate, NFFT=1024, noverlap=512, cmap='inferno')
    plt.title("Espectrograma de Áudio")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Frequência (Hz)")
    plt.colorbar(label='Intensidade')
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()
    return caminho

# ----------------------------
# MEMÓRIA INTERNA SIMPLIFICADA
# ----------------------------
memoria_estado = {
    "sistemas": {
        "servidor_auth": "operacional",
        "banco_dados": "operacional"
    },
    "historico_eventos": []
}

# ----------------------------
# RESPOSTAS REATIVAS
# ----------------------------
def resposta_reativa(evento: Evento):
    if evento.tipo == "falha_sistema":
        sistema = evento.detalhes.get("sistema")
        memoria_estado["sistemas"][sistema] = "falho"
        return f"Alerta: {sistema} está fora do ar. Iniciando protocolo de contingência."
    elif evento.tipo == "ataque_cibernetico":
        return "Ataque detectado! Acionando time de segurança e bloqueando tráfego suspeito."
    else:
        return "Evento recebido. Aguardando análise."

# ----------------------------
# PLANEJAMENTO SIMPLIFICADO
# ----------------------------
def planejamento_deliberativo(evento: Evento):
    if evento.tipo == "falha_sistema":
        return [
            "Notificar equipe de TI",
            "Redirecionar tráfego para backup",
            "Gerar relatório para diretoria"
        ]
    elif evento.tipo == "ataque_cibernetico":
        return [
            "Isolar sistemas afetados",
            "Analisar logs",
            "Comunicar stakeholders"
        ]
    return ["Monitorar situação"]

# ----------------------------
# APRENDIZADO (simulado)
# ----------------------------
modelo_aprendizado = {
    "falha_sistema": "Prioridade Alta",
    "ataque_cibernetico": "Crítico"
}

def classificar_evento(evento: Evento):
    return modelo_aprendizado.get(evento.tipo, "Desconhecido")

# ----------------------------
# COMPARAÇÃO COM EVENTOS ANTERIORES
# ----------------------------
def comparar_com_eventos_passados(evento_atual: Evento):
    historico = memoria_estado["historico_eventos"]
    if not historico:
        return "Nenhum evento semelhante encontrado.", None

    documentos = [
        json.dumps(e['evento']) for e in historico
    ] + [json.dumps(evento_atual.dict())]

    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform(documentos)

    similaridades = cosine_similarity(tfidf[-1], tfidf[:-1])
    indice_mais_similar = np.argmax(similaridades)
    maior_similaridade = similaridades[0, indice_mais_similar]

    if maior_similaridade > 0.3:
        evento_similar = historico[indice_mais_similar]
        return f"Evento semelhante encontrado com similaridade {maior_similaridade:.2f}", evento_similar
    return "Nenhum evento semelhante encontrado.", None

# ----------------------------
# GERAÇÃO DE RELATÓRIO COM LLaMA
# ----------------------------
def gerar_relatorio_llama_local(evento: Evento, resposta: str, plano: list, prioridade: str):
    prompt = f"""
    Gere um relatório de crise:
    Evento: {evento.tipo}
    Origem: {evento.origem}
    Detalhes: {evento.detalhes}
    Resposta Reativa: {resposta}
    Plano de Ação: {plano}
    Prioridade: {prioridade}
    """

    try:
        response = requests.post("http://localhost:11434/api/generate", json={"model": "llama3.2", "prompt": prompt}, stream=True)
        relatorio_final = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line.decode("utf-8"))
                    relatorio_final += data.get("response", "")
                except Exception as e:
                    print("Erro ao decodificar linha do LLaMA:", e)
        return relatorio_final or "Relatório vazio."
    except Exception as e:
        return f"Erro ao gerar relatório com LLaMA Local: {e}"

# ----------------------------
# SALVAR RELATÓRIO EM ARQUIVO
# ----------------------------
def salvar_relatorio(relatorio: str, timestamp: str):
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = os.path.join(pasta, f"relatorio_crise_{timestamp}.txt")
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)
    return nome_arquivo

# ----------------------------
# ENVIO POR EMAIL
# ----------------------------
def enviar_email_relatorio(arquivo: str, destinatario: str):
    msg = EmailMessage()
    msg["Subject"] = "[Queto] Relatório de Crise Gerado"
    msg["From"] = os.getenv("EMAIL_ORIGEM")
    msg["To"] = destinatario

    with open(arquivo, "rb") as f:
        msg.add_attachment(f.read(), maintype="text", subtype="plain", filename=arquivo)

    with smtplib.SMTP(os.getenv("SMTP_SERVIDOR"), int(os.getenv("SMTP_PORTA"))) as smtp:
        smtp.starttls()
        smtp.login(os.getenv("EMAIL_ORIGEM"), os.getenv("EMAIL_SENHA"))
        smtp.send_message(msg)

# ----------------------------
# ENDPOINT PRINCIPAL
# ----------------------------
@app.post("/evento")
async def receber_evento(evento: Evento):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    memoria_estado["historico_eventos"].append({"evento": evento.dict(), "timestamp": timestamp})

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

# ----------------------------
# ENDPOINT PARA ÁUDIO
# ----------------------------
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

        signal_filtrado = filtro_passa_baixa(signal, rate)
        espectrograma_path = salvar_espectrograma(signal_filtrado, rate, timestamp)
        padrao = detectar_padroes(signal_filtrado, rate)

        evento = Evento(
            tipo="evento_audio",
            origem="sensor_audio",
            detalhes={"padrao_detectado": padrao, "arquivo_audio": file.filename}
        )

        resposta = resposta_reativa(evento)
        plano = planejamento_deliberativo(evento)
        prioridade = classificar_evento(evento)
        similaridade_msg, evento_similar = comparar_com_eventos_passados(evento)

        relatorio = gerar_relatorio_llama_local(evento, resposta, plano, prioridade)
        arquivo_txt = salvar_relatorio(relatorio, timestamp)
        enviar_email_relatorio(arquivo_txt, os.getenv("EMAIL_DESTINO"))

        return {
            "padrao_detectado": padrao,
            "resposta_reativa": resposta,
            "plano_acao": plano,
            "prioridade": prioridade,
            "relatorio": relatorio,
            "similaridade": similaridade_msg,
            "evento_similar": evento_similar,
            "espectrograma": espectrograma_path
        }
    finally:
        os.remove(caminho_temp)

# ----------------------------
# ROTA DE MONITORAMENTO
# ----------------------------
@app.get("/estado")
async def obter_estado():
    return memoria_estado
