import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
import datetime

def gravar_audio_microfone(duracao=10, samplerate=44100):
    print("Gravando áudio...")
    audio = sd.rec(int(duracao * samplerate), samplerate=samplerate, channels=1, dtype='int16')
    sd.wait()
    caminho_arquivo = f"audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    write(caminho_arquivo, samplerate, audio)
    print(f"Áudio salvo em {caminho_arquivo}")
    return caminho_arquivo

def reconhecer_fala(caminho_audio):
    recognizer = sr.Recognizer()
    with sr.AudioFile(caminho_audio) as source:
        audio = recognizer.record(source)
    try:
        texto = recognizer.recognize_google(audio, language="pt-BR")
        return texto
    except sr.UnknownValueError:
        return "Não foi possível reconhecer a fala."
    except sr.RequestError as e:
        return f"Erro na requisição ao serviço de reconhecimento: {e}"
