from sqlmodel import Session

from db import engine
from domain.entities import Ingrediente, Receita, ReceitaIngredienteLink


def main():
    with Session(engine) as session:
        ingrediente_acucar = Ingrediente(nome='Açúcar', peso=1000, custo=14)
        ingrediente_manteiga = Ingrediente(nome='Manteiga', peso=1000, custo=40)
        ingrediente_chocolate = Ingrediente(nome='Chocolate', peso=1000, custo=57)
        ingrediente_farinha = Ingrediente(nome='Farinha', peso=1000, custo=4)

        receita_cookies = Receita(nome='Cookies', peso_unitario=100)
        receita_cookies_ingrediente_acucar = ReceitaIngredienteLink(quantidade=100, receita=receita_cookies, ingrediente=ingrediente_acucar)
        receita_cookies_ingrediente_manteiga = ReceitaIngredienteLink(quantidade=100, receita=receita_cookies, ingrediente=ingrediente_manteiga)
        receita_cookies_ingrediente_chocolate = ReceitaIngredienteLink(quantidade=100, receita=receita_cookies, ingrediente=ingrediente_chocolate)
        receita_cookies_ingrediente_farinha = ReceitaIngredienteLink(quantidade=100, receita=receita_cookies, ingrediente=ingrediente_farinha)

        session.add(receita_cookies_ingrediente_acucar)
        session.add(receita_cookies_ingrediente_manteiga)
        session.add(receita_cookies_ingrediente_chocolate)
        session.add(receita_cookies_ingrediente_farinha)
        session.commit()


if __name__ == '__main__':
    main()
