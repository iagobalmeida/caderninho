from datetime import datetime
from random import randint

from sqlmodel import Session

from db import engine
from domain.entities import (Estoque, Ingrediente, Organizacao, Receita,
                             ReceitaIngredienteLink, Usuario, Venda)


def try_add(obj):
    try:
        with Session(engine) as session:
            __obj = session.add(obj)
            session.commit()
        return __obj
    except Exception as ex:
        return obj


def main():
    organizacao = Organizacao(descricao='Herbaria', usuarios=[
        Usuario(
            nome='Juliana Martello',
            email='julianamartello@gmail.com',
            senha='123',
            dono=True
        )
    ])
    try_add(organizacao)

    try_add(Usuario(
        nome='Administrador',
        email='admin@email.com',
        senha='admin',
        administrador=True,
        organizacao_id=2
    ))

    ingredientes = [1, 2, 3, 4]

    try_add(Ingrediente(organizacao_id=1, id=1, nome='Açúcar', peso=1000, custo=14))
    try_add(Ingrediente(organizacao_id=1, id=2, nome='Manteiga', peso=1000, custo=40))
    try_add(Ingrediente(organizacao_id=1, id=3, nome='Chocolate', peso=1000, custo=57))
    try_add(Ingrediente(organizacao_id=1, id=4, nome='Farinha', peso=1000, custo=4))

    try_add(Receita(organizacao_id=1, id=1, nome='Cookies', peso_unitario=100))

    try_add(Receita(organizacao_id=3, id=2, nome='Cookies Apenas ADMIN Vê', peso_unitario=100))

    for __ingrediente in ingredientes:
        try_add(ReceitaIngredienteLink(organizacao_id=1, quantidade=100, receita_id=1, ingrediente_id=__ingrediente))
        estoque_quantidade = randint(250, 2000) - randint(250, 2000)
        try_add(Estoque(
            organizacao_id=1,
            descricao='Compra' if estoque_quantidade > 0 else 'Uso em receita',
            ingrediente_id=__ingrediente,
            quantidade=estoque_quantidade,
            valor_pago=randint(1, 10) if estoque_quantidade > 0 else 0
        ))

    for _ in range(30):
        quantidade = randint(10, 20)
        data_criacao = datetime.now().replace(day=randint(1, 24), month=randint(1, 12))
        try_add(Venda(organizacao_id=1, descricao=f'{quantidade} x MiniCookies', valor=quantidade*12, data_criacao=data_criacao))


if __name__ == '__main__':
    main()
