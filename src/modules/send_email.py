import os
import smtplib
from email.mime.text import MIMEText
from typing import Any, List, Tuple, Union

from src.env import getenv

SMTP_LOGIN = getenv('SMTP_LOGIN', None)
SMTP_PASSWORD = getenv('SMTP_PASSWORD', None)


def enviar(assunto: str, corpo: str, para: List[str], smtp_login: str = SMTP_LOGIN, smtp_password: str = SMTP_PASSWORD) -> Tuple[Union[Exception, None], Any]:
    resultado = None
    exception = None

    try:
        mensagem = MIMEText(corpo)
        mensagem['Subject'] = assunto
        mensagem['From'] = SMTP_LOGIN
        mensagem['To'] = ','.join(para)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            resultado = smtp_server.login(smtp_login, smtp_password)
            resultado = smtp_server.sendmail(SMTP_LOGIN, para, mensagem.as_string())
    except Exception as ex:
        exception = ex

    return (exception, resultado)
