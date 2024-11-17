from datetime import datetime
from logging import getLogger
from typing import List, Tuple

from sqlmodel import Session, SQLModel, func, select

from src.domain.entities import (Estoque, Ingrediente, Receita,
                                 ReceitaIngredienteLink, Venda)

log = getLogger(__name__)


def __user_from_session(session: Session):
    sessao_usuario = session.info.get('user', {})
    return sessao_usuario


def __filter_organization_id(session: Session, query, entity: SQLModel):
    sessao_usuario = session.info.get('user', {})
    log.info(f'sessao_usuario: {sessao_usuario}')

    if sessao_usuario:
        usuario_administrador = sessao_usuario.get('administrador', False)
        organizacao_id = sessao_usuario.get('organizacao_id', -1)
        if usuario_administrador:
            return query
        log.info(f'organizacao_id: {organizacao_id}')
        return query.filter(entity.organizacao_id == organizacao_id)

    log.info(f'organizacao_id: -1')
    return query.filter(entity.organizacao_id == -1)


def __delete(session: Session, entity: SQLModel, id: int) -> bool:
    sessao_usuario = __user_from_session(session)
    sessao_usuario_admin = sessao_usuario.get('administrador', False)
    sessao_usuario_organizacao_id = int(sessao_usuario.get('organizacao_id', -1))

    db_entity = session.get(entity, id)

    if not db_entity:
        return True

    if not sessao_usuario_admin and not db_entity.organizacao_id == sessao_usuario_organizacao_id:
        raise ValueError('Sem permissão para deletar esse registro')

    session.delete(db_entity)
    session.commit()
    return True


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
    sessao_usuario = __user_from_session(session)
    sessao_usuario_admin = sessao_usuario.get('administrador', False)
    sessao_usuario_organizacao_id = int(sessao_usuario.get('organizacao_id', -1))

    db_entity = session.get(entity, id)
    if not sessao_usuario_admin and not db_entity.organizacao_id == sessao_usuario_organizacao_id:
        raise ValueError('Sem permissão para editar esse registro')

    for key, value in kwargs.items():
        if not value:
            continue
        db_entity.__setattr__(key, value)
    session.commit()
    return db_entity


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


def __create(session: Session, entity):
    sessao_usuario = __user_from_session(session)
    sessao_usuario_organizacao_id = sessao_usuario.get('organizacao_id', -1)

    entity.organizacao_id = sessao_usuario_organizacao_id

    session.add(entity)
    session.commit()
    return entity


def create_receita(session: Session, nome: str) -> Receita:
    return __create(session, Receita(nome=nome, peso_unitario=1, porcentagem_lucro=33))


def list_receitas(session: Session, filter_nome: str = None) -> List[Receita]:
    query = select(Receita)
    query = __filter_organization_id(session, query, Receita)

    if filter_nome:
        query = query.filter(Receita.nome.like(f'%{filter_nome}%'))
    receitas = session.exec(query).all()
    return receitas


def get_receita(session: Session, id: int) -> Receita:
    receita = session.get(Receita, id)
    return receita


def get_ingredientes(session: Session) -> List[Ingrediente]:
    query = select(Ingrediente)
    query = __filter_organization_id(session, query, Receita)

    ingredientes = session.exec(query).all()
    return ingredientes


def create_ingrediente(session: Session, nome: str, peso: float, custo: float) -> Ingrediente:
    organizacao_id = session.info.get('user', {}).get('organizacao_id')
    novo_ingrediente = Ingrediente(
        organizacao_id=organizacao_id,
        nome=nome,
        peso=peso,
        custo=custo
    )
    session.add(novo_ingrediente)
    session.commit()
    return novo_ingrediente


def create_receita_ingrediente(session: Session, receita_id: int, ingrediente_id: int, quantidade: float) -> ReceitaIngredienteLink:
    organizacao_id = session.info.get('user', {}).get('organizacao_id')
    receita_ingrediente = ReceitaIngredienteLink(
        organizacao_id=organizacao_id,
        receita_id=receita_id,
        ingrediente_id=ingrediente_id,
        quantidade=quantidade
    )
    session.add(receita_ingrediente)
    session.commit()
    return receita_ingrediente


def list_estoques(session: Session, filter_ingrediente_id: int = -1, filter_data_inicio: datetime = None, filter_data_final: datetime = None) -> List[Estoque]:
    query = select(Estoque)

    query = __filter_organization_id(session, query, Receita)

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

    query = __filter_organization_id(session, query, Receita)

    if filter_data_inicio:
        query = query.filter(Venda.data_criacao >= filter_data_inicio)

    if filter_data_final:
        query = query.filter(Venda.data_criacao <= filter_data_final)

    ret = session.exec(query.order_by(Venda.data_criacao.desc())).all()
    return ret


def create_venda(session: Session, descricao: str, valor: float) -> Venda:
    organizacao_id = session.info.get('user', {}).get('organizacao_id')
    venda = Venda(
        organizacao_id=organizacao_id,
        descricao=descricao,
        valor=valor
    )
    session.add(venda)
    session.commit()
    return venda


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
