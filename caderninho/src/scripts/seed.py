import asyncio
from datetime import datetime, timedelta
from random import choice, randint
from typing import Optional

from loguru import logger
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from caderninho.src import db
from caderninho.src.domain.entities import (
    CaixaMovimentacao,
    Estoque,
    Insumo,
    Organizacao,
    Receita,
    ReceitaGasto,
)
from caderninho.src.scripts import mocks


def __random_date(starting_off: datetime = datetime.now(), range: int = 30):
    return starting_off + timedelta(days=randint(range * -1, range))


async def try_add(session: AsyncSession, obj):
    try:
        # obj.id = None
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        if type(obj).__name__ in [
            # "Insumo",
            "Usuario"
        ]:
            logger.info(obj)
        return obj
    except Exception as ex:
        logger.error(str(ex))
        await session.rollback()
        return obj


async def try_get_organizacao(
    session: AsyncSession, cnpj: str
) -> Optional[Organizacao]:
    try:
        organizacao = (
            await session.exec(select(Organizacao).where(Organizacao.cnpj == cnpj))
        ).first()
        return organizacao
    except Exception as ex:
        logger.error(str(ex))
        await session.rollback()
        return None


async def mocked_main(session: AsyncSession):

    async with db.init_session() as session:
        existing_organizacao = await try_get_organizacao(
            session, cnpj=mocks.MOCK_ORGANIZACAO.cnpj
        )
        if existing_organizacao:
            logger.error("Organização base já criada")
            return

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

        acucar = await try_add(
            session,
            Insumo(organizacao_id=organizacao.id, nome="Açúcar", peso=1000, custo=14),
        )
        manteiga = await try_add(
            session,
            Insumo(organizacao_id=organizacao.id, nome="Manteiga", peso=1000, custo=40),
        )
        chocolate = await try_add(
            session,
            Insumo(
                organizacao_id=organizacao.id, nome="Chocolate", peso=1000, custo=57
            ),
        )
        farinha = await try_add(
            session,
            Insumo(organizacao_id=organizacao.id, nome="Farinha", peso=1000, custo=4),
        )
        insumos = [acucar, manteiga, chocolate, farinha, insumo_mock]

        for __insumo in insumos:
            await try_add(
                session,
                ReceitaGasto(
                    organizacao_id=organizacao.id,
                    quantidade=100,
                    receita_id=cookies.id,
                    insumo_id=__insumo.id,
                ),
            )
            estoque_quantidade = randint(-100, 100)
            await try_add(
                session,
                Estoque(
                    data_criacao=__random_date(),
                    organizacao_id=organizacao.id,
                    descricao=(
                        "Compra"
                        if estoque_quantidade > 0
                        else f"Uso em receita ({cookies.nome})"
                    ),
                    insumo_id=__insumo.id,
                    quantidade=estoque_quantidade,
                    valor_pago=randint(1, 10) if estoque_quantidade > 0 else 0,
                ),
            )
        logger.info("Adicionando custo percentual")
        await try_add(
            session,
            ReceitaGasto(
                organizacao_id=organizacao.id,
                receita_id=cookies.id,
                descricao="Gasto percentual",
                gasto_tipo="PERCENTUAL",
                gasto_valor=10,
            ),
        )

        logger.info("Adicionando custo fixo")
        await try_add(
            session,
            ReceitaGasto(
                organizacao_id=organizacao.id,
                receita_id=cookies.id,
                descricao="Gasto fixo",
                gasto_tipo="FIXO",
                gasto_valor=2,
            ),
        )

        for _ in range(60):
            data_criacao = __random_date()
            if randint(1, 3) >= 2:
                quantidade = randint(-200, -1)
                insumo = choice(insumos)
                quantidade *= -1
                await try_add(
                    session,
                    Estoque(
                        data_criacao=data_criacao,
                        organizacao_id=organizacao.id,
                        descricao=(
                            "Compra"
                            if quantidade > 0
                            else f"Uso em receita ({cookies.nome})"
                        ),
                        insumo_id=insumo.id,
                        quantidade=quantidade,
                        valor_pago=randint(8, 50) if quantidade > 0 else 0,
                    ),
                )
            if randint(1, 3) >= 2:
                quantidade = randint(1, 10)
                await try_add(
                    session,
                    CaixaMovimentacao(
                        organizacao_id=organizacao.id,
                        descricao=f"{quantidade} x MiniCookies",
                        valor=quantidade * 12,
                        data_criacao=data_criacao,
                    ),
                )
        await session.close()


async def herbaria(session: AsyncSession):
    existing_organizacao = await try_get_organizacao(
        session, cnpj=mocks.MOCK_ORGANIZACAO.cnpj
    )
    if existing_organizacao:
        logger.error("Organização base já criada")
        return

    organizacao = await try_add(session, mocks.MOCK_ORGANIZACAO)

    mocks.MOCK_USUARIO_DONO.organizacao_id = organizacao.id
    mocks.MOCK_USUARIO_SENHA_RECUPERADA.organizacao_id = organizacao.id

    await try_add(session, mocks.MOCK_USUARIO_DONO)
    await try_add(session, mocks.MOCK_USUARIO_SENHA_RECUPERADA)
    await try_add(session, mocks.MOCK_USUARIO_ADMIN)

    insumos = [
        Insumo(nome="açucar confeiteiro", custo=7.00, peso=500),  # 0
        Insumo(nome="açucar cristal", custo=5.00, peso=1000),  # 1
        Insumo(nome="açúcar glacê real", custo=21.90, peso=1000),  # 2
        Insumo(nome="Açúcar mascavo", custo=9.00, peso=500),  # 3
        Insumo(nome="adoçante", custo=43.00, peso=400),  # 4
        Insumo(nome="bala gelatina dentadura", custo=3.75, peso=35),  # 6
        Insumo(nome="bala gelatina mini dentadura", custo=1.50, peso=15),  # 7
        Insumo(nome="banana", custo=7.00, peso=1000),  # 8
        Insumo(nome="Baunilha", custo=12.00, peso=800),  # 9
        Insumo(nome="Bicarbonato", custo=18.00, peso=1000),  # 10
        Insumo(nome="biscoito triturado Negresco", custo=49.90, peso=1000),  # 11
        Insumo(nome="brigadeiro branco", custo=49.47, peso=3315),  # 12
        Insumo(nome="brigadeiro caramelo", custo=55.80, peso=3315),  # 13
        Insumo(nome="brigadeiro de limão", custo=9.45, peso=550),  # 14
        Insumo(nome="brigadeiro meio amargo", custo=52.12, peso=3395),  # 15
        Insumo(nome="brigadeiro cookies'n cream", custo=54.60, peso=3430),  # 16
        Insumo(nome="brookie", custo=32.36, peso=1197),  # 17
        Insumo(nome="cacau em pó 50%", custo=33.90, peso=600),  # 18
        Insumo(nome="canela em pó", custo=5.00, peso=50),  # 19
        Insumo(nome="caramelo dadinho", custo=19.90, peso=660),  # 20
        Insumo(nome="cereja em calda", custo=21.90, peso=125),  # 21
        Insumo(nome="chantilly", custo=26.89, peso=1000),  # 22
        Insumo(nome="chocolate branco gotas SICAO", custo=119.90, peso=1010),  # 23
        Insumo(nome="chocolate ao leite gotas SICAO", custo=109.90, peso=1010),  # 24
        Insumo(nome="chocolate meio amargo barra NESTLÉ", custo=99.90, peso=1000),  # 25
        Insumo(nome="chocolate meio amargo gotas SICAO", custo=119.90, peso=1010),  # 26
        Insumo(nome="cobertura ao leite barra SICAO", custo=39.90, peso=1010),  # 27
        Insumo(nome="cobertura branco barra SICAO", custo=46.90, peso=1010),  # 28
        Insumo(nome="cobertura meio amargo barra SICAO", custo=42.90, peso=1010),  # 29
        Insumo(nome="cocada cremosa", custo=54.13, peso=3115),  # 30
        Insumo(nome="cocada meio amargo", custo=64.79, peso=3395),  # 31
        Insumo(nome="coco ralado", custo=22.90, peso=800),  # 32
        Insumo(nome="concentrado natural de limão", custo=0.96, peso=5),  # 33
        Insumo(nome="confeito coração", custo=7.50, peso=170),  # 34
        Insumo(nome="confeito colorido halloween", custo=1.50, peso=18),  # 35
        Insumo(nome="cookie all black", custo=3.87, peso=120),  # 36
        Insumo(nome="cookie ao leite", custo=2.91, peso=90),  # 37
        Insumo(nome="cookie nutella", custo=5.42, peso=120),  # 38
        Insumo(nome="cookie red velvet", custo=2.47, peso=90),  # 39
        Insumo(nome="cookie sem chocolate (só massa),", custo=14.48, peso=765),  # 40
        Insumo(nome="corante preto", custo=5.90, peso=25),  # 41
        Insumo(nome="corante verde", custo=5.90, peso=25),  # 42
        Insumo(nome="corante vermelho", custo=6.50, peso=25),  # 43
        Insumo(nome="creme de avelã carrefour", custo=51.99, peso=700),  # 44
        Insumo(nome="creme de avelã nutella", custo=59.90, peso=650),  # 45
        Insumo(nome="creme de leite", custo=2.49, peso=200),  # 46
        Insumo(nome="creme de ninho", custo=96.09, peso=1450),  # 47
        Insumo(nome="doce de leite", custo=20.00, peso=900),  # 48
        Insumo(nome="farinha de trigo", custo=5.00, peso=1000),  # 49
        Insumo(nome="farinha de aveia", custo=9.49, peso=500),  # 50
        Insumo(nome="fermento quimico", custo=11.00, peso=250),  # 51
        Insumo(nome="geléia frutas vermelhas", custo=12.00, peso=350),  # 52
        Insumo(nome="geléia morango", custo=30.00, peso=500),  # 53
        Insumo(nome="gengibre em pó", custo=5.00, peso=15),  # 54
        Insumo(nome="glucose de milho", custo=30.00, peso=500),  # 55
        Insumo(nome="granulado natalino", custo=6.90, peso=150),  # 56
        Insumo(nome="iogurte natural", custo=4.00, peso=170),  # 57
        Insumo(nome="kinder bueno barrinha", custo=6.00, peso=40),  # 58
        Insumo(nome="leite", custo=5.00, peso=1000),  # 59
        Insumo(nome="leite condensado", custo=6.00, peso=395),  # 60
        Insumo(nome="leite em pó", custo=60.00, peso=1000),  # 61
        Insumo(nome="limão taiti", custo=5.00, peso=1000),  # 62
        Insumo(nome="lotus biscoito", custo=18.90, peso=124),  # 63
        Insumo(nome="maltodextrol", custo=20.90, peso=400),  # 64
        Insumo(nome="Manteiga", custo=40.00, peso=1000),  # 65
        Insumo(nome="marshmallow", custo=7.00, peso=220),  # 66
        Insumo(nome="mini cookies", custo=3.88, peso=120),  # 67
        Insumo(nome="MMs", custo=37.00, peso=1000),  # 68
        Insumo(nome="morango", custo=16.00, peso=500),  # 69
        Insumo(nome="Negresco", custo=3.50, peso=90),  # 70
        Insumo(nome="noz moscada", custo=8.00, peso=8),  # 71
        Insumo(nome="óleo vegetal", custo=8.00, peso=1000),  # 72
        Insumo(nome="ovo", custo=22.00, peso=1000),  # 73
        Insumo(nome="Oreo mini", custo=4.40, peso=35),  # 74
        Insumo(nome="recheio sabor choc ao leite GOTAS", custo=39.90, peso=1010),  # 75
        Insumo(nome="recheio sabor choc ao leite PASTA", custo=39.90, peso=1010),  # 76
        Insumo(nome="recheio sabor avelã PASTA", custo=46.90, peso=1010),  # 77
        Insumo(nome="recheio sabor choc branco GOTAS", custo=46.90, peso=1010),  # 78
        Insumo(nome="recheio sabor ninho", custo=1.72, peso=25.00),  # 79
        Insumo(nome="recheio sabor pistache PASTA", custo=41.90, peso=1010),  # 80
        Insumo(nome="sal", custo=4.00, peso=1000),  # 81
        Insumo(nome="stikadinho", custo=1.00, peso=12),  # 82
        Insumo(nome="stiksy salgadinho", custo=10.00, peso=160),  # 83
    ]

    for _insumo in insumos:
        _insumo.nome = _insumo.nome.title()
        _insumo.organizacao_id = organizacao.id
        await try_add(session, _insumo)

    receitas = [
        (
            Receita(
                organizacao_id=organizacao.id,
                nome="Sanduíche de Brownie",
                peso_unitario=150,
                peso_perda_por_processo=70,
                porcentagem_lucro=37,
            ),
            [(73, 150), (1, 270), (72, 120), (18, 85), (49, 90), (38, 240)],
        )
    ]
    for _receita, _gastos in receitas:
        receita = await try_add(session, _receita)
        for insumo_id, quantidade in _gastos:
            await try_add(
                session,
                ReceitaGasto(
                    receita_id=receita.id,
                    organizacao_id=organizacao.id,
                    insumo_id=insumos[insumo_id].id,
                    descricao="Uso em receita",
                    gasto_valor=0,
                    gasto_tipo=None,
                    quantidade=quantidade,
                ),
            )

    await session.close()


async def main():
    async with db.init_session() as session:

        await herbaria(session=session)


if __name__ == "__main__":
    asyncio.run(main())
