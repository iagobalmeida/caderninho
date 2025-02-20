import re

SOBRE_ESSA_PAGINA = {
    'home': [
        'Nessa página existem três caixas com valores monetários: `Entradas`, `Saídas` e `Caixa`.',
        '`Entradas` é a soma de todas as suas vendas.',
        '`Saídas` é a soma de todas as suas movimentações de compra ou gasto.',
        '`Caixa` é a diferença entre `Entradas` e `Saídas` (`Caixa = Entradas Saídas`).',
        'Nessa página existe uma caixa que exibe o `QR PIX` da última venda, caso a venda esteja como `Não Recebida (Pendente)`.',
        'Além disso existem caixas que exibem o número total de registros e um atalho para as outras páginas.',
        '<a href="/app/como_usar">Como usar</a>',
    ],
    'vendas': [
        'Uma `Venda` é composta por uma `Data`, uma `Descrição`, um `Valor` e uma configuração que define se a venda já foi `Recebida`.',
        'Toda venda é criada como `Não Recebida (Pendente)` e você pode atualizar isso clicando em uma venda ou selecionando várias e usando as ações `Marcar como Pendente`/`Marcar como Recebido`. (Também existe um atalho na página `Home` para atualizar a última venda).',
        '<a href="/app/como_usar/#como_usar_venda">4.1. O que é uma venda</a>',
        '<a href="/app/como_usar/#como_usar_cadastrar_venda">4.2. Cadastrando uma venda</a>',
        '<a href="/app/como_usar/#como_usar_qr_pix">4.3. Gerando um QR PIX</a>',
        '<a href="/app/como_usar/#como_usar_receber_pagamento">4.4. Recebendo um Pagamento</a>'
    ],
    'estoques': [
        'Uma `Movimentação` pode ser de 4 tipos: `Compra`, `Consumo Insumo`, `Uso em Receita` e `Outros`.',
        '`Compra` representa a compra de um `Insumo`, por isso irá aumentar o estoque.',
        '`Consumo Insumo` representa o consumo de um `Insumo` (fora de uma receita), então não possuí `Valor Pago` e irá diminuir o estoque.',
        '`Uso em Receita` representa o consumo de todos os `Insumos` que fazem parte de uma `Receita`, facilitando o cadastro de produções de receitas. Irá diminuir o estoque.',
        '`Outros` representa qualquer outro gasto que não afete o estoque.',
        '<a href="/app/como_usar/#como_usar_movimentacao">2.1. O que é uma movimentação</a>',
        '<a href="/app/como_usar/#como_usar_cadastrar_compra">2.2. Cadastrando uma Movimentação de Compra</a>',
    ],
    'receitas': [
        'Cadastrar uma `Receita` te permite calcular de forma intuitiva o custo de produção, a quantidade de insumos necessários, o valor de venda, etc.',
        'Uma `Receita` é composta por uma lista de `Insumos` e duas configurações: `Peso Unitário` e `Porcetagem de Lucro`.',
        '`Peso Unitário` é onde você cadastra peso de cada unidade que a receita produz (Se a receita produz apenas uma unidade, preencha com o mesmo valor do campo `Rendimento`).',
        '`Porcetagem de Lucro` é onde você cadastra qual a porcetagem de lucro que você deseja usar no cáclulo de preço.',
        'Após preencher a lista de `Insumos` e as duas configurações, você poderá verificar em `Estimativas` e `Precificação` os valores cálculados.',
        '<a href="/app/como_usar/#como_usar_1_1">1.1. O que é uma receita</a>',
        '<a href="/app/como_usar/#como_usar_precificacao">1.2.1. Precificação</a>',
        '<a href="/app/como_usar/#como_usar_estimativas">1.2.2. Estimativas</a>',
        '<a href="/app/como_usar/#como_usar_cadastrar_receita">1.3. Cadastrando uma Receita</a>',
    ],
    'insumos': [
        'Um `Insumo` pode representar tanto um ingrediente quanto uma embalagem ou qualquer material necessário para produzir uma `Receita`.',
        'Cada `Insumo` tem um custo fixo, mas o sistema também cálcula automáticamente (baseado em suas `Movimentações` de `Compra`) o `Custo Méd.`, sendo esse a média dos preços pagos por esse `Insumo`.',
        'Atualmente o sistema contempla duas unidades de medida: `g (Gramas)` e `un (Unidades)`.',
        '<a href="/app/como_usar">Como usar</a>',
    ],
    'organizacao': [
        'Organização é a representação da sua empresa dentro do KDerninho.',
        'As `Configurações` te permitem modificar o comportamento do painel para todos os usuários da sua organização.',
        'É possível gerenciar os acessos e privilégios dos usuários em `Usuários`.',
        '<a href="/app/como_usar">Como usar</a>',
    ]
}


def get_sobre_essa_pagina_html(nome_pagina: str):
    conteudo = SOBRE_ESSA_PAGINA.get(nome_pagina, None)
    if not conteudo:
        return None

    linhas = [
        f'<p class="mb-1 text-muted">{"-" if not "<a href" in linha else ""} {linha}</p>'
        for linha in conteudo
    ]
    conteudo = '\n'.join(linhas)
    conteudo = re.sub(r"`(.*?)`", r"<code>\1</code>", conteudo)
    conteudo = re.sub(r"__(.*?)__", r"<i>\1</i>", conteudo)
    return conteudo
