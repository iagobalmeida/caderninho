import smtplib
from unittest.mock import patch

from src.modules import send_email
from src.tests.mocks import MockSMTPServer, MockSMTPServerException


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
