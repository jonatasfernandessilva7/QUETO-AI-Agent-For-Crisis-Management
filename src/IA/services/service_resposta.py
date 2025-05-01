from src.IA.modelos import Evento
from src.IA.memoria import memoria_estado
import requests
import os

def resposta_reativa(evento: Evento):
    if evento.tipo == "falha_sistema":
        sistema = evento.detalhes.get("sistema")
        memoria_estado["sistemas"][sistema] = "falho"
        return f"Alerta: {sistema} está fora do ar. Iniciando protocolo de contingência."
    elif evento.tipo == "ataque_cibernetico":
        return "Ataque detectado! Acionando time de segurança e bloqueando tráfego suspeito."
    else:
        return "Evento recebido. Aguardando análise."

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

def gerar_resposta_llama_local(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    modelo = os.getenv("llama3.2:latest", "llama3.2") 

    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False 
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        resposta = response.json()["response"]
        return resposta.strip()
    except Exception as e:
        print(f"Erro ao gerar resposta do modelo: {e}")
        return "Erro ao gerar resposta com a IA."