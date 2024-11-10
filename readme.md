# CADERNINHO

## Introdução
Esse SAAS foi desenvolvido para auxiliar minha companheira na gestão de sua loja de cookies.

O Sistema conta capacidade para múltiplas contas e organizações e permite gerenciar:
- Receitas
- Ingredientes
- Estoque (Entradas/Saídas)
- Vendas (Saídas)

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

## TODO
- [ ] Cadastrar movimentação de estoque a partir de `receita_id` e `quantidade_produzida`
- [ ] Remover tela `Ingredientes (confusa)`

