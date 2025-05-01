from src.IA.services.service_resposta import gerar_resposta_llama_local

modelo_aprendizado = {
    "falha_sistema": "Prioridade Alta",
    "ataque_cibernetico": "Crítico",
    "Explosão": "Crítico"
}

def classificar_evento(detalhes_evento):
    prompt = f"""
    You are an AI specialized in corporate risks and crises. Your task is to identify and classify events based on input data, which may include audio, text, images, or other formats.

    Based on the **event details** below, classify the type of event using **only one word** (e.g., Explosion, Siren, Gunshot, Scream, Alarm, Cyberattack, etc.).

    **Event Details:** {detalhes_evento}

    **Respond with only the event type, as a single word, in Portuguese.**
    """
    resposta = gerar_resposta_llama_local(prompt)
    return resposta.strip()
