import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

memoria_estado = {
    "sistemas": {
        "servidor_auth": "operacional",
        "banco_dados": "operacional"
    },
    "historico_eventos": []
}

def comparar_com_eventos_passados(evento_atual):
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

def obter_historico_eventos():
    return memoria_estado["historico_eventos"]

def adicionar_evento_historico(evento):
    memoria_estado["historico_eventos"].append(evento)

def obter_estado_memoria():
    return memoria_estado

def clusterizar_eventos(historico, k=3):
    if len(historico) < k:
        return {"erro": f"Número de clusters {k} maior que eventos disponíveis."}

    textos = [json.dumps(ev["evento"]) for ev in historico]

    vetorizar = TfidfVectorizer()
    vetores = vetorizar.fit_transform(textos)

    modelo = KMeans(n_clusters=k, random_state=42)
    labels = modelo.fit_predict(vetores)

    agrupados = {}
    for idx, label in enumerate(labels):
        agrupados.setdefault(f"cluster_{label}", []).append(historico[idx]["evento"])

    return agrupados