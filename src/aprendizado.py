from modelos import Evento
import requests
import os

modelo_aprendizado = {
    "falha_sistema": "Prioridade Alta",
    "ataque_cibernetico": "Crítico",
    "Explosão": "Crítico"
}

def gerar_resposta_llama_local(prompt: str) -> str:
    url = "http://localhost:11434/api/generate"
    modelo = os.getenv("llama3.2:latest", "llama3.2") 

    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False  # False para receber a resposta toda de uma vez
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        resposta = response.json()["response"]
        return resposta.strip()
    except Exception as e:
        print(f"Erro ao gerar resposta do modelo: {e}")
        return "Erro ao gerar resposta com a IA."



def classificar_evento(detalhes_evento):
    prompt = f"""
    Você é uma IA especializada em identificar tipos de eventos a partir de dados de áudio.  
    Com base nos seguintes detalhes, classifique o tipo do evento em uma palavra (ex: Explosão, Sirene, Tiro, Grito, Alarme, etc.).

    Detalhes do evento: {detalhes_evento}

    Resposta apenas com o tipo:
    """
    resposta = gerar_resposta_llama_local(prompt)
    return resposta.strip()
