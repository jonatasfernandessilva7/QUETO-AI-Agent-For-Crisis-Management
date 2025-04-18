from modelos import Evento

modelo_aprendizado = {
    "falha_sistema": "Prioridade Alta",
    "ataque_cibernetico": "Crítico"
}

def classificar_evento(evento: Evento):
    return modelo_aprendizado.get(evento.tipo, "Desconhecido")