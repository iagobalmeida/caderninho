import re

SOBRE_ESSA_PAGINA = {
    'home': [
        'Nessa página existem três caixas com valores monetários: `Entradas`, `Saídas` e `Caixa`.',
        '`Entradas` é a soma de todas as suas vendas.',
        '`Saídas` é a soma de todas as suas movimentações de compra ou gasto.',
        '`Caixa` é a diferença entre `Entradas` e `Saídas` (`Caixa = Entradas Saídas`).',
        'Nessa página existe uma caixa que exibe o `QR PIX` da última venda, caso a venda esteja como `Não Recebida (Pendente)`.',
        'Além disso existem caixas que exibem o número total de registros e um atalho para as outras páginas.',
    ],
    'vendas': [
        'Uma `Venda` é composta por uma `Data`, uma `Descrição`, um `Valor` e uma configuração que define se a venda já foi `Recebida`.',
        'Toda venda é criada como `Não Recebida (Pendente)` e você pode atualizar isso clicando em uma venda ou selecionando várias e usando os botões acima. (Também existe um atalho na página `Home` para atualizar a última venda).',
    ],
    'estoques': [
        'Uma `Movimentação` pode ser de 4 tipos: `Compra`, `Consumo Insumo`, `Uso em Receita` e `Outros`.',
        '`Compra` representa a compra de um `Insumo`, por isso irá aumentar o estoque.',
        '`Consumo Insumo` representa o consumo de um `Insumo` (fora de uma receita), então não possuí `Valor Pago` e irá diminuir o estoque.',
        '`Uso em Receita` representa o consumo de todos os `Insumos` que fazem parte de uma `Receita`, facilitando o cadastro de produções de receitas. Irá diminuir o estoque.',
        '`Outros` representa qualquer outro gasto que não afete o estoque.',
    ],
    'receitas': [
        'Cadastrar uma `Receita` te permite calcular de forma intuitiva o custo de produção, a quantidade de insumos necessários, o valor de venda, etc.',
        'Uma `Receita` é composta por uma lista de `Insumos` e duas configurações: `Peso Unitário` e `Porcetagem de Lucro`.',
        '`Peso Unitário` é onde você cadastra peso de cada unidade que a receita produz (Se a receita produz apenas uma unidade, preencha com o mesmo valor do campo `Rendimento`).',
        '`Porcetagem de Lucro` é onde você cadastra qual a porcetagem de lucro que você deseja usar no cáclulo de preço.',
        'Após preencher a lista de `Insumos` e as duas configurações, você poderá verificar em `Estimativas` e `Precificação` os valores cálculados.',
    ],
    'insumos': [
        'Um `Insumo` pode representar tanto um ingrediente quanto uma embalagem ou qualquer material necessário para produzir uma `Receita`.',
        'Cada `Insumo` tem um custo fixo, mas o sistema também cálcula automáticamente (baseado em suas `Movimentações` de `Compra`) o `Custo Méd.`, sendo esse a média dos preços pagos por esse `Insumo`.',
        'Atualmente o sistema contempla duas unidades de medida: `g (Gramas)` e `un (Unidades)`.',
    ],
    'organizacao': [
        'Organização é a representação da sua empresa dentro do KDerninho.',
        'As `Configurações` te permitem modificar o comportamento do painel para todos os usuários da sua organização.',
        'É possível gerenciar os acessos e privilégios dos usuários em `Usuários`.',
    ]
}


def get_sobre_essa_pagina_html(nome_pagina: str):
    conteudo = SOBRE_ESSA_PAGINA.get(nome_pagina, None)
    if not conteudo:
        return None

    linhas = [
        f'<p class="mb-1 text-muted">- {linha}</p>'
        for linha in conteudo
    ] + [
        f'<p class="mb-1 text-muted">Se ficou com mais alguma dúvida, <a href="/app/documentacao#{nome_pagina}" class="text-primary cursor-pointer">clique aqui para acessar a documentação completa</a>.</p>'
    ]
    conteudo = '\n'.join(linhas)
    conteudo = re.sub(r"`(.*?)`", r"<code>\1</code>", conteudo)
    conteudo = re.sub(r"__(.*?)__", r"<i>\1</i>", conteudo)
    return conteudo
