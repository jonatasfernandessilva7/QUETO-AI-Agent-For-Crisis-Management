import requests
import os
import json
import re

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.platypus import Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from src.IA.modelos import Evento

def gerar_relatorio_llama_local(evento: Evento, resposta: str, plano: list, prioridade: str):
    prompt = f"""
You are an expert in corporate risks and crisis management. Based on the information provided, generate a detailed **risk and crisis report in Portuguese**, following **ABNT formatting rules**.

The report must be:
- Visually well-structured and easy to understand.
- Written in formal tone, with **technical terminology** where appropriate.
- Free of irrelevant information or noise.
- Focused on describing **possible crises** that may arise from the detected **event**.

Use the following structured data:

{{
  "event": "{evento.tipo}",
  "source": "{evento.origem}",
  "details": "{evento.detalhes}",
  "reactive_answer": "{resposta}",
  "action_plan": {json.dumps(plano, ensure_ascii=False)},
  "priority": "{prioridade}"
}}

**Report Requirements:**
- Include a clear description of the event and its context.
- Explain potential risks and escalation scenarios.
- Develop the **action_plan** based on the principles of **ISO 22361:2022** (Crisis Management) and **ISO 31000:2018** (Risk Management).
- Classify the **priority level** of the event using the **color-coded system from ISO 22324:2022** (e.g., Low, Moderate, High, Very High, Extreme).
- End the report by stating the **confidence level** or **accuracy** of the analysis, values always in **percentage**.

Do not include comments or explanations outside the report content.

Write the entire response in **Portuguese**, maintaining a professional, calm, and expert tone.
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
    pasta = "../relatorios"
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = os.path.join(pasta, f"relatorio_crise_{timestamp}.pdf")

    doc = SimpleDocTemplate(nome_arquivo, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()

    cor_alerta = get_color_by_prioridade(prioridade)
    estilo_prioridade = ParagraphStyle(
        name="Prioridade",
        parent=styles["Heading2"],
        textColor=cor_alerta,
        fontSize=16,
        spaceAfter=12
    )

    story = []

    story.append(Paragraph("📘 <b>QUETO - Relatório</b>", styles["Title"]))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"<b>Prioridade:</b> {prioridade}", estilo_prioridade))
    story.append(Spacer(1, 12))

    for linha in relatorio.strip().split("\n"):
        if linha.strip():
            linha_formatada = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", linha.strip())
            story.append(Paragraph(linha_formatada, styles["Normal"]))
            story.append(Spacer(1, 6))
    
    caminho_img = f"../image/matriz_alerta_iso22324.png"
    story.append(Spacer(1, 12))
    story.append(Paragraph("<b>Código de Cores de Alerta Baseado na ISO 22324:</b>", styles["Normal"]))
    story.append(Spacer(1, 6))
    story.append(RLImage(caminho_img, width=16*cm, height=2*cm))
    

    doc.build(story)
    return nome_arquivo