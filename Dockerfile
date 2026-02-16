FROM python:3.12-slim

# Configurações de ambiente para Python
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instala dependências de sistema (gcc, etc) necessárias para compilar pacotes
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala o poetry
RUN pip install --no-cache-dir poetry

# Copia arquivos de dependências e o readme (necessário se citado no pyproject.toml)
COPY pyproject.toml poetry.lock readme.md ./

# Instala as dependências do projeto
# --without dev: Não instala dependências de teste/dev para produção
# --no-root: Não instala o pacote atual como lib (o código será copiado depois)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --without dev

# Copia o restante do código da aplicação
COPY . .

# Comando de execução: usa a variável $PORT do Railway ou 8000 como padrão
CMD ["sh", "-c", "uvicorn caderninho.src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]