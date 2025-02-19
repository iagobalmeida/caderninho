from datetime import datetime
from random import randint

from sqlmodel import Session

from src.db import engine
from src.domain.entities import (Estoque, Insumo, Organizacao, Receita,
                                 ReceitaInsumoLink, Usuario, Venda)


def try_add(obj):
    try:
        with Session(engine) as session:
            __obj = session.add(obj)
            session.commit()
            session.refresh(__obj)
        return __obj
    except Exception as ex:
        print(ex)
        return obj


def main():
    try_add(Organizacao(descricao='Herbaria', cidade='Caxias do Sul', chave_pix='347.753.508-11', usuarios=[Usuario(
        nome='Usuário',
        email='usuario@email.com',
        senha='123',
        dono=True
    )]))

    try_add(Usuario(
        nome='Administrador',
        email='admin@email.com',
        senha='admin',
        administrador=True
    ))

    acucar = try_add(Insumo(organizacao_id=1, nome='Açúcar', peso=1000, custo=14))
    manteiga = try_add(Insumo(organizacao_id=1, nome='Manteiga', peso=1000, custo=40))
    chocolate = try_add(Insumo(organizacao_id=1, nome='Chocolate', peso=1000, custo=57))
    farinha = try_add(Insumo(organizacao_id=1, nome='Farinha', peso=1000, custo=4))

    cookies = try_add(Receita(organizacao_id=1, nome='Cookies', peso_unitario=100))

    cookies_admin = try_add(Receita(organizacao_id=3, nome='Cookies Apenas ADMIN Vê', peso_unitario=100))

    for __insumo in [acucar, manteiga, chocolate, farinha]:
        try_add(ReceitaInsumoLink(organizacao_id=1, quantidade=100, receita_id=1, insumo_id=__insumo.id))
        estoque_quantidade = randint(250, 2000) - randint(250, 2000)
        try_add(Estoque(
            organizacao_id=1,
            descricao='Compra' if estoque_quantidade > 0 else 'Uso em receita',
            insumo_id=__insumo.id,
            quantidade=estoque_quantidade,
            valor_pago=randint(1, 10) if estoque_quantidade > 0 else 0
        ))

    for _ in range(30):
        quantidade = randint(10, 20)
        data_criacao = datetime.now().replace(day=randint(1, 24), month=randint(1, 12))
        try_add(Venda(organizacao_id=1, descricao=f'{quantidade} x MiniCookies', valor=quantidade*12, data_criacao=data_criacao))


if __name__ == '__main__':
    main()
