import os
import smtplib
from email.mime.text import MIMEText
from typing import List

SMTP_LOGIN = os.getenv('SMTP_LOGIN', None)
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', None)


def enviar(assunto: str, corpo: str, de: str, para: List[str], smtp_login: str = SMTP_LOGIN, smtp_password: str = SMTP_PASSWORD) -> bool:
    mensagem = MIMEText(corpo)
    mensagem['Subject'] = assunto
    mensagem['From'] = de
    mensagem['To'] = ','.join(para)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(smtp_login, smtp_password)
        smtp_server.sendmail(de, para, mensagem.as_string())
    return True
