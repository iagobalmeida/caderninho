import smtplib
from unittest.mock import patch

from src.modules import send_email


class MockSMTPServer():
    def __enter__(self, *args, **kwargs):
        return self  # Retorna a própria instância para ser usada no with

    def __exit__(self, *args, **kwargs):
        pass  # Nada a fazer ao sair do contexto

    def login(self, *args, **kwargs):
        return True

    def sendmail(self, *args, **kwargs):
        return True


class MockSMTPServerException(MockSMTPServer):
    def login(self, *args, **kwargs):
        raise ValueError('Erro teste')


def test_send_email_enviar():
    with patch.object(smtplib, 'SMTP_SSL', return_value=MockSMTPServer()):
        exception, result = send_email.enviar(
            assunto='Teste',
            corpo='Teste de email',
            para=['iago.almeida@gmail.com'],
            smtp_login='foo',
            smtp_password='bar'
        )
    assert not exception
    assert result


def test_send_email_enviar_invalido():
    with patch.object(smtplib, 'SMTP_SSL', return_value=MockSMTPServerException()):
        exception, result = send_email.enviar(
            assunto='Teste',
            corpo='Teste de email',
            para=['iago.almeida@gmail.com'],
            smtp_login='foo',
            smtp_password='bar'
        )
    assert exception
    assert not result
