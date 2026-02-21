FROM python:3.12-alpine

RUN apk add --no-cache build-base libpq postgresql-dev curl

RUN pip install poetry

WORKDIR /app

COPY ./pyproject.toml ./poetry.lock .

RUN poetry config virtualenvs.create false \
&& poetry install --only main --no-root

COPY ./caderninho caderninho

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "caderninho.src.app:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]