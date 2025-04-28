import requests
import os
import json

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from modelos import Evento

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


def get_color_by_prioridade(prioridade):
    cores = {
        "Crítico": colors.red,
        "Prioridade Alta": colors.orange,
        "Moderado": colors.yellow,
        "Baixo": colors.green,
        "Desconhecido": colors.gray
    }
    return cores.get(prioridade, colors.gray)

def salvar_relatorio(relatorio: str, timestamp: str, prioridade="Desconhecido"):
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = os.path.join(pasta, f"relatorio_crise_{timestamp}.pdf")

    # Documento PDF
    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    # Estilo personalizado para destaque de prioridade
    cor_alerta = get_color_by_prioridade(prioridade)
    estilo_prioridade = ParagraphStyle(
        name="Prioridade",
        parent=styles["Heading2"],
        textColor=cor_alerta,
        fontSize=16,
        spaceAfter=12
    )

    story = []

    # Título principal
    story.append(Paragraph("📘 <b>Relatório de Crise</b>", styles["Title"]))
    story.append(Spacer(1, 12))

    # Destaque visual da prioridade com cor ISO 22324
    story.append(Paragraph(f"<b>Prioridade:</b> {prioridade}", estilo_prioridade))
    story.append(Spacer(1, 12))

    # Conteúdo do relatório
    for linha in relatorio.strip().split("\n"):
        if linha.strip():
            story.append(Paragraph(linha.strip(), styles["Normal"]))
            story.append(Spacer(1, 6))

    doc.build(story)
    return nome_arquivo
