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
- Gerenciar o estoque de seus insumos e outros insumos
- Gerenciar seu fluxo de caixa cadastrando compras, produção de receitas e outros gastos em geral
- Compartilhar essas informações com outros usuários de sua organização (⚙ Em desenvolvimento)
- Exportar e importar dados em CSV (⚙ Em desenvolvimento)

## Como Usar

### Instalação
1. Crie um ambiente virtual com `python3 -m venv .venv`
2. Inicie o ambiente virtual cmo `source ./.venv/bin/activate`
3. Instale as bibliotecas necessárias com `pip install -r requirements.txt`

### Execução
1. Inicie a aplicação com `uvicorn src.app:app --reload`

### Rodando localmente com dados de exemplo
1. Inicie a aplicação
2. Acesse `127.0.0.1:8000/docs`
3. Execute a rota `/seed` para criar dados de testes no banco
4. Use a conta `usuario@emai.com` com a senha `123` para acessar como usuário
5. Use a conta `admin@email.com` com a senha `admin` para acessar como admin

### Testes
```
coverage run -m pytest && coverage html
```

## vb1.0
- [X] Separar `scripts.js`
- [X] Ajustar exibição de datas em modais
- [X] Permitir valores quebrados em inputs
- [X] Cadastrar movimentação de estoque a partir de `receita_id` e `quantidade_produzida`
- [X] Cadastrar quantidade positiva/negativa em estoque a partir de descrição
- [X] Remover tela `Insumos` (confusa)
- [X] Usar clique em linha em vez de `editar/excluir`
- [X] Adicionar checkbox com delete massivo em tabelas
    - [X] Vendas
    - [X] Estoques
    - [X] Receitas
        - [X] Listagem
        - [X] Insumos
- [X] Adicionar opção excluir em modal de `editar`
    - [X] Vendas
    - [X] Estoque
    - [X] Receitas
        - [X] Listagem
        - [X] Insumos

## vb1.1
- [X] Melhorar UX para mobile
- [X] Bloquear acesso sem login (decorator)
- [X] Padronizar botão `Ações` contendo `Criar` e `Apagar`
- [X] Adicionar confirmação para sair
- [X] Encontrar lugar para editar nome de insumo
- [X] Maior robustes em delete/update para garantir organization_id
- [X] Autenticação em fluxos de `seed`
- [X] Ajustar redirect de erro

## vb1.8
- [X] Melhorar `db.py`
- [X] Modal `Meu Perfil`
- [X] Novo layout
  - [X] Admin
  - [X] Toggle modo escuro/claro
  - [X] Login

## vb2.0
- [X] Formulários verticais em modal
- [X] Padronizar método `dict()` em entidades para preencher `data-bs-payload`
  - [X] Atualizar JS para pegar `data-bs-payload` de `tr` ao clicar em `td`
  - [X] Padronizar formatação de YYYY-MM-DD
- [X] Aperfeiçoar ainda mais modal e criação e edição de Estoque
- [X] Funcionalidade modal `Meu Perfil`
- [X] Padronizar uso de `HEADER_AUTH` em vez de decorator
  - [X] Apagar decorator
- [-] Upload e download de CSV (Próxima versão)
- [-] Tela "Organização" (Próxima versão)

## vb2.5
- [X] Tela "sobre a aplicação"
- [X] Corrigir modal de perfil
- [X] Corrigir inputs de data
- [X] Tela de criação de conta
  - [X] Funcionalidade criação de conta + organização
  - [X] Bloqueio organizações com mesmo nome
- [X] Tela "Organização"
  - [X] Alterar nome da organização
  - [X] Criar usuário
  - [X] Apagar usuário
  - [X] Criar usuário dono
  - [X] Limitar ações para apenas donos
  - [X] Editar usuário
    - [X] Modal
    - [X] Funcionalidade
- [X] Alterar senha
  - [X] Modal
  - [X] Funcionalidade
- [X] Reorganizar rotas
- [X] Expiração de Sessão login
- [X] Redirecionamento de acordo com status_code
- [X] Permitindo organizações com mesmo nome
- [X] Refatorar `auth.py`
- [X] Reestruturar sesão autorizada de banco de dados
- [X] Alertas de sucesso
- [X] Padronização de termos (criar, atualizar, excluír, incluir e remover)
- [X] Unificar modal "deleteSelecionados"
- [X] Funcionalidade esqueci minha senha
- [X] "Lembrar de mim neste dispositivo"
- [X] Melhorar `repository.py`
  - [X] Unificar verificacao de permissões
  - [X] Unificar fluxos repetitivos

# v1.0
- [X] Geração de QR Code p/ chave PIX da organização
  - [X] Geração de QR Code PIX com valor da venda
  - [X] Campos `cidade` e `chave_pix` em Organização
    - [X] Atualização dos campos a partir de tela `/organização`
    - [X] Geração de QR Code última venda com dados da organização
- [X] Campo `paga` em venda
- [X] Melhorar `repository.py`
- [X] Menu "Ações" mobile
- [X] Ação `marcar como paga` em vendas
- [X] Ação `marcar como paga` em home
- [X] Atalho para `marcar como paga` em Home
- [X] Modularização de tabelas
  - [X] Template `table.html` genérico
  - [X] Método `columns` e `row` em entidades
  - [X] Modularizar modal
  - [X] Remoção `.../table.html`
  - [X] Contempla `href` para Receitas
  - [X] Contempla "insumos" de Receita

# v1.2
- [X] Gestão de insumos
  - [X] Exibir receitas associadas em Insumo
  - [X] Exibir estoque atual em insumos
- [X] Configurações em Organização
  - [X] Card colapsavel de configurações
  - [X] Campos JSON em banco de dados
  - [X] Rota de atualização / assocaição com tela
  - [X] Aplicar filtro de medida de acordo com config
  - [X] Aplicar filtro de medida geral de acordo com config
  - [X] Aplicar calculos baseados em custo med/g de acordo com config
- [X] Collapse em QR Code home
- [X] Reorganização de templates
- [X] Paginação em tabelas
- [X] Reorganização de roteadores
  - [X] Criação de Schemas

# v1.3
- [X] Ingredientes viraram Insumos
  - [X] Permitir unidades em insumos (gramas e unidade)
  - [X] Atualizar calculo de receitas
- [X] Ajustar contexto e sessão
- [X] Ajustar informações dashboard

# v1.4
- [X] Melhoria descrição de movimentação `Uso em Receita`
- [X] Instalação de `loguru` para logs em arquivo rotativo e logs aprimorados
- [X] Alerta "Sobre essa página" com link para documentação completa
  - [X] Home
  - [X] Vendas
  - [X] Estoque
  - [X] Receitas
  - [X] Detalhe de Receita
  - [X] Insumos
  - [X] Organização
- [X] Documentação completa agregando todas as docs
  - [X] Referências para docs completa
- [X] Tornar alerta "apagavel" (metadata de usuário em JSON talvez?)
  - [X] LocalStorage deu conta do recado

# v1.4.5
- [ ] Testes unitários de todas as rotas do sistema

# v1.5
- [ ] Gerar QR PIX em detalhamento de vendas
- [ ] Campo `plano` em Organização
  - [ ] Limitar número de registros por plano em `create`
  - [ ] Exibir plano atual
  - [ ] Botão para upgrade de plano

# v2.0
- [ ] Filtro em tabelas
- [ ] Geração de QR Code PIX com valor customizado
- [ ] Upload e download de CSV
