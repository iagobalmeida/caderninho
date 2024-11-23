from datetime import datetime
from logging import getLogger
from typing import List, Tuple

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, func, select

from src.auth import usuario_de_sessao_db
from src.domain.entities import (Estoque, Ingrediente, Organizacao, Receita,
                                 ReceitaIngredienteLink, Usuario, Venda)

log = getLogger(__name__)


def __filter_organization_id(session: Session, query, entity: SQLModel):
    sessao_usuario = usuario_de_sessao_db(session)
    if sessao_usuario.administrador:
        return query
    return query.filter(entity.organizacao_id == sessao_usuario.organizacao_id)


def __delete(session: Session, entity: SQLModel, id: int) -> bool:
    db_entity = session.get(entity, id)
    if not db_entity:
        return True

    sessao_usuario = usuario_de_sessao_db(session)
    if not sessao_usuario.administrador and not db_entity.organizacao_id == sessao_usuario.organizacao_id:
        raise ValueError('Sem permissão para deletar esse registro')

    session.delete(db_entity)
    session.commit()
    return True


def delete_usuario(session: Session, id: int) -> bool:
    return __delete(session, Usuario, id)


def delete_receita(session: Session, id: int) -> bool:
    return __delete(session, Receita, id)


def delete_receita_ingrediente(session: Session, id: int) -> bool:
    return __delete(session, ReceitaIngredienteLink, id)


def delete_venda(session: Session, id: int) -> bool:
    return __delete(session, Venda, id)


def delete_estoque(session: Session, id: int) -> bool:
    return __delete(session, Estoque, id)


def delete_ingrediente(session: Session, id: int) -> bool:
    links_receitas = session.exec(select(ReceitaIngredienteLink).where(ReceitaIngredienteLink.ingrediente_id == id)).all()
    for link in links_receitas:
        session.delete(link)
    return __delete(session, Ingrediente, id)


def __update(session: Session, entity: SQLModel, id: int, **kwargs) -> SQLModel:
    db_entity = session.get(entity, id)
    if not db_entity:
        raise ValueError(f'{entity.__name__} com id {id} não encontrado')

    sessao_usuario = usuario_de_sessao_db(session)

    if not sessao_usuario.administrador and not db_entity.organizacao_id == sessao_usuario.organizacao_id:
        raise ValueError('Sem permissão para editar esse registro')

    for key, value in kwargs.items():
        if not value:
            continue
        db_entity.__setattr__(key, value)

    session.commit()
    return db_entity


def update_organizacao(session: Session, id: int, descricao: str):
    db_organizacao = session.get(Organizacao, id)
    sessao_usuario = usuario_de_sessao_db(session)

    if not (sessao_usuario.dono and sessao_usuario.organizacao_id == db_organizacao.id):
        raise ValueError('Sem permissão para editar a organização')

    db_organizacao.descricao = descricao
    session.commit()
    return db_organizacao


def update_receita(session: Session, id: int, nome: str, peso_unitario: float, porcentagem_lucro: float) -> Receita:
    return __update(session, Receita, id, nome=nome, peso_unitario=peso_unitario, porcentagem_lucro=porcentagem_lucro)


def update_ingrediente(session: Session, id: int, nome: str = None, peso: float = None, custo: float = None) -> Ingrediente:
    return __update(session, Ingrediente, id, nome=nome, peso=peso, custo=custo)


def update_receita_ingrediente(session: Session, id: int, quantidade: float) -> ReceitaIngredienteLink:
    return __update(session, ReceitaIngredienteLink, id, quantidade=quantidade)


def update_venda(session: Session, id: int, descricao: str, valor: float) -> Venda:
    return __update(session, Venda, id, descricao=descricao, valor=valor)


def update_estoque(session: Session, id: int, descricao: str, valor_pago: float = None, quantidade: float = None, ingrediente_id: float = None) -> Estoque:
    return __update(session, Estoque, id, descricao=descricao, valor_pago=valor_pago, quantidade=quantidade, ingrediente_id=ingrediente_id)


def update_organizacao_usuario(session: Session, id: int, nome: str, email: str, dono: bool, senha: str = None):
    if senha:
        return __update(session, Usuario, id, nome=nome, email=email, dono=dono, senha=senha)
    else:
        return __update(session, Usuario, id, nome=nome, email=email, dono=dono)


def update_usuario_senha(session: Session, id: int, senha_atual: str, senha: str, senha_confirmar: str):
    usuario = session.exec(select(Usuario).where(Usuario.id == id)).first()
    sessao_usuario = usuario_de_sessao_db(session)

    if usuario.id != sessao_usuario.id:
        raise ValueError('Sem permissão para alterar a senha desse usuário')

    if not usuario:
        raise ValueError('Usuário não encontrado')

    if usuario.senha != senha_atual:
        raise ValueError('Senha atual inválida')

    if senha != senha_confirmar:
        raise ValueError('As senhas não batem')

    usuario.senha = senha
    session.commit()
    return usuario


def __create(session: Session, entity):
    sessao_usuario = usuario_de_sessao_db(session)
    entity.organizacao_id = sessao_usuario.organizacao_id
    session.add(entity)
    session.commit()
    return entity


def create_usuario(session: Session, nome: str, email: str, senha: str, organizacao_descricao: str = None, organizacao_id: int = None, dono: bool = False):
    '''Envie `organizacao_nome` para criar uma nova organização / Envie `organizacao_id` para associar o usuário a uma organização existente'''
    db_organizacao_id = None

    if organizacao_id:
        db_organizacao = session.exec(select(Organizacao).where(Organizacao.id == organizacao_id)).first()
    elif organizacao_descricao:
        db_organizacao = Organizacao(descricao=organizacao_descricao)
        session.add(db_organizacao)
        session.commit()

    db_organizacao_id = db_organizacao.id

    db_usuario = Usuario(nome=nome, email=email, senha=senha, organizacao_id=db_organizacao_id, dono=dono)
    session.add(db_usuario)
    session.commit()
    return db_usuario


def create_receita(session: Session, nome: str) -> Receita:
    return __create(session, Receita(nome=nome, peso_unitario=1, porcentagem_lucro=33))


def create_ingrediente(session: Session, nome: str, peso: float, custo: float) -> Ingrediente:
    return __create(session, Ingrediente(
        nome=nome,
        peso=peso,
        custo=custo
    ))


def create_receita_ingrediente(session: Session, receita_id: int, ingrediente_id: int, quantidade: float) -> ReceitaIngredienteLink:
    return __create(session, ReceitaIngredienteLink(
        receita_id=receita_id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    ))


def create_venda(session: Session, descricao: str, valor: float) -> Venda:
    return __create(session,  Venda(
        descricao=descricao,
        valor=valor
    ))


def create_estoque(session: Session, descricao: str, ingrediente_id: int = None, quantidade: float = None, valor_pago: float = None) -> Estoque:
    if not ingrediente_id and not quantidade and not valor_pago:
        return False
    if ingrediente_id == -1:
        ingrediente_id = None
    if not quantidade:
        quantidade = None

    db_estoque = Estoque(
        descricao=descricao,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade,
        valor_pago=valor_pago
    )
    __create(session, db_estoque)
    return True


def list_receitas(session: Session, filter_nome: str = None) -> List[Receita]:
    query = select(Receita)
    query = __filter_organization_id(session, query, Receita)

    if filter_nome:
        query = query.filter(Receita.nome.like(f'%{filter_nome}%'))
    receitas = session.exec(query).all()
    return receitas


def list_estoques(session: Session, filter_ingrediente_id: int = -1, filter_data_inicio: datetime = None, filter_data_final: datetime = None) -> List[Estoque]:
    query = select(Estoque)

    query = __filter_organization_id(session, query, Estoque)

    if filter_ingrediente_id and filter_ingrediente_id != -1:
        query = query.filter(Estoque.ingrediente_id == filter_ingrediente_id)

    if filter_data_inicio:
        query = query.filter(Estoque.data_criacao >= filter_data_inicio)

    if filter_data_final:
        query = query.filter(Estoque.data_criacao <= filter_data_final)

    query = query.order_by(Estoque.data_criacao.desc())

    return session.exec(query).all()


def list_vendas(session: Session, filter_data_inicio: datetime = None, filter_data_final: datetime = None) -> List[Venda]:
    query = select(Venda)

    query = __filter_organization_id(session, query, Venda)

    if filter_data_inicio:
        query = query.filter(Venda.data_criacao >= filter_data_inicio)

    if filter_data_final:
        query = query.filter(Venda.data_criacao <= filter_data_final)

    ret = session.exec(query.order_by(Venda.data_criacao.desc())).all()
    return ret


def get_fluxo_caixa(session: Session) -> Tuple[float, float, float]:
    query_entradas = select(func.sum(Venda.valor))
    query_entradas = __filter_organization_id(session, query_entradas, Venda)
    entradas = session.exec(query_entradas).first()

    query_saidas = select(func.sum(Estoque.valor_pago))
    query_saidas = __filter_organization_id(session, query_saidas, Estoque)
    saidas = session.exec(query_saidas).first()

    if not entradas and entradas != 0:
        entradas = 0

    if not saidas and saidas != 0:
        saidas = 0

    caixa = entradas - saidas
    return (entradas, saidas, caixa)


def get_receita(session: Session, id: int) -> Receita:
    query = __filter_organization_id(session, select(Receita).where(Receita.id == id), Receita)
    receita = session.exec(query).first()
    return receita


def get_ingredientes(session: Session) -> List[Ingrediente]:
    query = __filter_organization_id(session, select(Ingrediente), Receita)
    ingredientes = session.exec(query).all()
    return ingredientes


def get_usuarios(session: Session) -> List[Usuario]:
    query = __filter_organization_id(session, select(Usuario), Usuario)
    usuarios = session.exec(query).all()
    return usuarios


def get_organizacao(session: Session, id: int) -> Organizacao:
    query = select(Organizacao).where(Organizacao.id == id)
    organizacao = session.exec(query).first()
    return organizacao
