from modelos import Evento
from memoria import memoria_estado

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