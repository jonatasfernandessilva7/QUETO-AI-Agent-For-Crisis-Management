from modelos import Evento
from resposta import gerar_resposta_llama_local

modelo_aprendizado = {
    "falha_sistema": "Prioridade Alta",
    "ataque_cibernetico": "Crítico",
    "Explosão": "Crítico"
}

def classificar_evento(detalhes_evento):
    prompt = f"""
    Você é uma IA especializada riscos e crises corporativas. Você deve identificar eventos a partir de entradas em áudio, texto, imagens, entre outros.  
    Com base nos seguintes detalhes, classifique o tipo do evento em uma palavra (ex: Explosão, Sirene, Tiro, Grito, Alarme, Ataque Cibernético etc.).

    Detalhes do evento: {detalhes_evento}

    Resposta apenas com o tipo:
    """
    resposta = gerar_resposta_llama_local(prompt)
    return resposta.strip()
