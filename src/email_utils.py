import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

def enviar_email_relatorio(arquivo: str, destinatario: str):
    msg = EmailMessage()
    msg["Subject"] = "[Queto] Relatório de Crise Gerado"
    msg["From"] = os.getenv("EMAIL_ORIGEM")
    msg["To"] = destinatario

    with open(arquivo, "rb") as f:
        msg.add_attachment(f.read(), maintype="text", subtype="plain", filename=arquivo)

    with smtplib.SMTP(os.getenv("SMTP_SERVIDOR"), int(os.getenv("SMTP_PORTA"))) as smtp:
        smtp.starttls()
        smtp.login(os.getenv("EMAIL_ORIGEM"), os.getenv("EMAIL_SENHA"))
        smtp.send_message(msg)