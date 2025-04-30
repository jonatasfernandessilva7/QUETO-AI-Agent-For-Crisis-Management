import soundfile as sf
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter
import matplotlib.pyplot as plt
import os

def analisar_som_fourier(file):
    try:
        data, samplerate = sf.read(file.file) #lê o som
        if len(data.shape) > 1: #transforma de estério pra mono se for preciso (verifica o número de canais, 2 canais == estéreo)
            data = data[:, 0]
        N = len(data) #número de amostras do áudio
        yf = fft(data) #transforma o áudio de domínio do tempo para o domínio da frequência
        xf = fftfreq(N, 1 / samplerate) #calcula os valores da frequência a cada componente da FFT
        idx = np.where(xf > 0) #remove as frequências negativas e calcula o módulo da FFT de cada frequência
        frequencias = xf[idx]
        amplitudes = np.abs(yf[idx])
        pico_frequencia = frequencias[np.argmax(amplitudes)] #encontra o índice de maior intensidade dentro do espectro/frequência com maior presença no som
        pico_amplitude = np.max(amplitudes) #intensidade da frequência
        return {
            "pico_frequencia": float(pico_frequencia),
            "pico_amplitude": float(pico_amplitude),
            "status": "analisado"
        }
    except Exception as e:
        return {"erro": str(e)}

def filtro_passa_baixa(signal, rate, cutoff=4000):
    nyquist = 0.5 * rate
    normal_cutoff = cutoff / nyquist
    b, a = butter(6, normal_cutoff, btype='low', analog=False)
    return lfilter(b, a, signal)

def detectar_padroes(signal, rate):
    energia = np.sum(signal ** 2)
    if energia > 1e12:
        return "Explosão detectada"
    elif np.mean(np.abs(signal)) > 1000:
        return "Grito ou alarme detectado"
    else:
        return "Ambiente calmo ou desconhecido"

def salvar_espectrograma(signal, rate, timestamp): #gera o espectograma
    pasta = "relatorios"
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, f"espectrograma_{timestamp}.png")
    plt.figure(figsize=(10, 4))
    plt.specgram(signal, Fs=rate, NFFT=1024, noverlap=512, cmap='inferno')
    plt.title("Espectrograma de Áudio")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Frequência (Hz)")
    plt.colorbar(label='Intensidade')
    plt.tight_layout()
    plt.savefig(caminho)
    plt.close()
    return caminho