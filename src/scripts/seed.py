import asyncio
from datetime import datetime, timedelta
from random import choice, randint

from loguru import logger
from sqlmodel.ext.asyncio.session import AsyncSession

import db
from domain.entities import (CaixaMovimentacao, Estoque, GastoRecorrente,
                             Insumo, Receita, ReceitaGasto)
from tests import mocks


def __random_date(starting_off: datetime = datetime.now(), range: int = 30):
    return starting_off + timedelta(days=randint(range*-1, range))


async def try_add(session: AsyncSession, obj):
    try:
        # obj.id = None
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        if type(obj).__name__ == 'Usuario':
            logger.info(obj)
        return obj
    except Exception as ex:
        logger.error(str(ex))
        await session.rollback()
        return obj


async def main():
    async with db.init_session() as session:
        organizacao = await try_add(session, mocks.MOCK_ORGANIZACAO)

        mocks.MOCK_USUARIO_DONO.organizacao_id = organizacao.id
        mocks.MOCK_USUARIO_SENHA_RECUPERADA.organizacao_id = organizacao.id

        await try_add(session, mocks.MOCK_USUARIO_DONO)
        await try_add(session, mocks.MOCK_USUARIO_SENHA_RECUPERADA)
        await try_add(session, mocks.MOCK_USUARIO_ADMIN)

        insumo_mock = await try_add(session, mocks.MOCK_INSUMO)
        cookies = await try_add(session, mocks.MOCK_RECEITA)

        await try_add(session, mocks.MOCK_ESTOQUE)
        await try_add(session, mocks.MOCK_GASTO_RECORRENTE_SALARIO_MOTOBY)
        await try_add(session, mocks.MOCK_GASTO_RECORRENTE_ALUGUEL)
        await try_add(session, mocks.MOCK_GASTO_RECORRENTE_TRIBUTOS)

        acucar = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Açúcar', peso=1000, custo=14))
        manteiga = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Manteiga', peso=1000, custo=40))
        chocolate = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Chocolate', peso=1000, custo=57))
        farinha = await try_add(session, Insumo(organizacao_id=organizacao.id, nome='Farinha', peso=1000, custo=4))

        insumos = [acucar, manteiga, chocolate, farinha, insumo_mock]

        for __insumo in insumos:
            await try_add(session, ReceitaGasto(organizacao_id=organizacao.id, quantidade=100, receita_id=cookies.id, insumo_id=__insumo.id))
            estoque_quantidade = randint(-100, 100)
            await try_add(session, Estoque(
                data_criacao=__random_date(),
                organizacao_id=organizacao.id,
                descricao='Compra' if estoque_quantidade > 0 else f'Uso em receita ({cookies.nome})',
                insumo_id=__insumo.id,
                quantidade=estoque_quantidade,
                valor_pago=randint(1, 10) if estoque_quantidade > 0 else 0
            ))
        logger.info('Adicionando custo percentual')
        await try_add(session, ReceitaGasto(
            organizacao_id=organizacao.id,
            receita_id=cookies.id,
            descricao='Gasto percentual',
            gasto_tipo='PERCENTUAL',
            gasto_valor=10
        ))

        logger.info('Adicionando custo fixo')
        await try_add(session, ReceitaGasto(
            organizacao_id=organizacao.id,
            receita_id=cookies.id,
            descricao='Gasto fixo',
            gasto_tipo='FIXO',
            gasto_valor=2
        ))

        for _ in range(60):
            data_criacao = __random_date()
            if randint(1, 3) >= 2:
                quantidade = randint(-200, -1)
                insumo = choice(insumos)
                quantidade *= -1
                await try_add(session, Estoque(
                    data_criacao=data_criacao,
                    organizacao_id=organizacao.id,
                    descricao='Compra' if quantidade > 0 else f'Uso em receita ({cookies.nome})',
                    insumo_id=insumo.id,
                    quantidade=quantidade,
                    valor_pago=randint(8, 50) if quantidade > 0 else 0
                ))
            if randint(1, 3) >= 2:
                quantidade = randint(1, 10)
                await try_add(session, CaixaMovimentacao(organizacao_id=organizacao.id, descricao=f'{quantidade} x MiniCookies', valor=quantidade*12, data_criacao=data_criacao))
        await session.close()

if __name__ == '__main__':
    asyncio.run(main())
