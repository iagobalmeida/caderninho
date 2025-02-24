from datetime import datetime
from random import randint

from loguru import logger
from sqlmodel import Session

from src.db import engine
from src.domain.entities import (Estoque, Insumo, Receita, ReceitaInsumoLink,
                                 Usuario, Venda)
from src.tests import mocks


def try_add(obj):
    try:
        obj.id = None

        with Session(engine) as session:
            session.add(obj)
            session.commit()
            session.refresh(obj)
            if type(obj).__name__ == 'Usuario':
                logger.info(obj)
            logger.info(f'{type(obj).__name__} #{obj.id} inserido')
        return obj
    except Exception as ex:
        logger.exception(ex)
        return obj


def main():
    organizacao = try_add(mocks.MOCK_ORGANIZACAO)
    try_add(mocks.MOCK_USUARIO_DONO)
    try_add(mocks.MOCK_USUARIO_ADMIN)
    try_add(mocks.MOCK_ESTOQUE)

    acucar = try_add(Insumo(organizacao_id=organizacao.id, nome='Açúcar', peso=1000, custo=14))
    manteiga = try_add(Insumo(organizacao_id=organizacao.id, nome='Manteiga', peso=1000, custo=40))
    chocolate = try_add(Insumo(organizacao_id=organizacao.id, nome='Chocolate', peso=1000, custo=57))
    farinha = try_add(Insumo(organizacao_id=organizacao.id, nome='Farinha', peso=1000, custo=4))
    cookies = try_add(Receita(organizacao_id=organizacao.id, nome='Cookies', peso_unitario=100))

    for __insumo in [acucar, manteiga, chocolate, farinha]:
        try_add(ReceitaInsumoLink(organizacao_id=organizacao.id, quantidade=100, receita_id=cookies.id, insumo_id=__insumo.id))
        estoque_quantidade = 75
        try_add(Estoque(
            organizacao_id=organizacao.id,
            descricao='Compra' if estoque_quantidade > 0 else f'Uso em receita ({cookies.nome})',
            insumo_id=__insumo.id,
            quantidade=estoque_quantidade,
            valor_pago=randint(1, 10) if estoque_quantidade > 0 else 0
        ))

    for _ in range(30):
        quantidade = randint(10, 20)
        data_criacao = datetime.now().replace(day=randint(1, 24), month=randint(1, 12))
        try_add(Venda(organizacao_id=organizacao.id, descricao=f'{quantidade} x MiniCookies', valor=quantidade*12, data_criacao=data_criacao))


if __name__ == '__main__':
    main()
