![# KDERNIHO](./src/static//logo.svg)

#### SASS para gestão simplificada da sua cozinha independente

## Introdução

Essa aplicação não seria possível seu a existência de:
- [Python](https://python.org)
- [SQLModel](https://github.com/fastapi/sqlmodel)
- [TablerCSS](https://tabler.io/)
- [Railwai.app](https://railway.app/)

### Funcionalidades

No lugar de tabelas do excel, você pode usar o KDerninho para:
- Estimar custo, faturamento e lucro de receitas de forma dinâmica
- Gerenciar o estoque de seus ingredientes e outros insumos
- Gerenciar seu fluxo de caixa cadastrando compras, produção de receitas e outros gastos em geral
- Compartilhar essas informações com outros usuários de sua organização (⚙ Em desenvolvimento)
- Exportar e importar dados em CSV (⚙ Em desenvolvimento)

## Como Usar

### Instalação
1. Crie um ambiente virtual com `python3 -m venv .venv`
2. Inicie o ambiente virtual cmo `source ./.venv/bin/activate`
3. Instale as bibliotecas necessárias com `pip install -r requirements.txt`

### Execução
1. Inicie a aplicação com `uvicorn src.app:app`

### Testes
1. Inicie a aplicação
2. Acesse `127.0.0.1:8000/docs`
3. Execute a rota `/seed` para criar dados de testes no banco
4. Use a conta `usuario@emai.com` com a senha `123` para acessar como usuário
5. Use a conta `admin@email.com` com a senha `admin` para acessar como admin

## TODO v1.0
- [X] Separar `scripts.js`
- [X] Ajustar exibição de datas em modais
- [X] Permitir valores quebrados em inputs
- [X] Cadastrar movimentação de estoque a partir de `receita_id` e `quantidade_produzida`
- [X] Cadastrar quantidade positiva/negativa em estoque a partir de descrição
- [X] Remover tela `Ingredientes` (confusa)
- [X] Usar clique em linha em vez de `editar/excluir`
- [X] Adicionar checkbox com delete massivo em tabelas
    - [X] Vendas
    - [X] Estoques
    - [X] Receitas
        - [X] Listagem
        - [X] Ingredientes
- [X] Adicionar opção excluir em modal de `editar`
    - [X] Vendas
    - [X] Estoque
    - [X] Receitas
        - [X] Listagem
        - [X] Ingredientes

## TODO v1.1
- [X] Melhorar UX para mobile
- [X] Bloquear acesso sem login (decorator)
- [X] Padronizar botão `Ações` contendo `Criar` e `Apagar`
- [X] Adicionar confirmação para sair
- [X] Encontrar lugar para editar nome de ingrediente
- [X] Maior robustes em delete/update para garantir organization_id
- [X] Autenticação em fluxos de `seed`
- [X] Ajustar redirect de erro

## TODO v1.8
- [X] Melhorar `db.py`
- [X] Modal `Meu Perfil`
- [X] Novo layout
  - [X] Admin
  - [X] Toggle modo escuro/claro
  - [X] Login

## TODO v2.0
- [ ] Formulários verticais em modal
- [ ] Padronizar método `dict()` em entidades para preencher `data-bs-payload`
- [ ] Funcionalidade modal `Meu Perfil`
- [ ] Upload e download de CSV
- [ ] Tela "Organização"

## TODO v2.5
- [ ] Tela de criação de conta
- [ ] Geração de QR Code p/ chave PIX da organização
- [ ] Possível integração com Mercado Pago
