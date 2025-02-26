import asyncio
from datetime import datetime
from random import randint

from loguru import logger

from src import db
from src.domain.entities import (Estoque, Insumo, Receita, ReceitaInsumoLink,
                                 Venda)
from src.tests import mocks


async def try_add(session, obj):
    try:
        obj.id = None
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        if type(obj).__name__ == 'Usuario':
            logger.info(obj)
        logger.info(f'{type(obj).__name__} #{obj.id} inserido')
        return obj
    except Exception as ex:
        logger.exception(ex)
        return obj


async def main():
    async with db.init_session() as session:
        organizacao = await try_add(session, mocks.MOCK_ORGANIZACAO)
        await try_add(session, mocks.MOCK_USUARIO_DONO)
        await try_add(session, mocks.MOCK_USUARIO_SENHA_RECUPERADA)
        await try_add(session, mocks.MOCK_USUARIO_ADMIN)
        await try_add(session, mocks.MOCK_ESTOQUE)

        acucar = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Açúcar', peso=1000, custo=14))
        manteiga = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Manteiga', peso=1000, custo=40))
        chocolate = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Chocolate', peso=1000, custo=57))
        farinha = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Farinha', peso=1000, custo=4))
        cookies = await try_add(session, Receita(organizacao_id=organizacao.id, nome='Cookies', peso_unitario=100))

        for __insumo in [acucar, manteiga, chocolate, farinha]:
            await try_add(session, ReceitaInsumoLink(organizacao_id=organizacao.id, quantidade=100, receita_id=cookies.id, insumo_id=__insumo.id))
            estoque_quantidade = 75
            await try_add(session, Estoque(
                organizacao_id=organizacao.id,
                descricao='Compra' if estoque_quantidade > 0 else f'Uso em receita ({cookies.nome})',
                insumo_id=__insumo.id,
                quantidade=estoque_quantidade,
                valor_pago=randint(1, 10) if estoque_quantidade > 0 else 0
            ))

        for _ in range(30):
            quantidade = randint(10, 20)
            data_criacao = datetime.now().replace(day=randint(1, 24), month=randint(1, 12))
            await try_add(session, Venda(organizacao_id=organizacao.id, descricao=f'{quantidade} x MiniCookies', valor=quantidade*12, data_criacao=data_criacao))
        await session.close()

if __name__ == '__main__':
    asyncio.run(main())
