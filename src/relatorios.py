import requests
import os
import json
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

def salvar_relatorio(relatorio: str, timestamp: str):
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)
    nome_arquivo = os.path.join(pasta, f"relatorio_crise_{timestamp}.txt")
    with open(nome_arquivo, "w", encoding="utf-8") as f:
        f.write(relatorio)
    return nome_arquivo