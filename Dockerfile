FROM python:3.11.9
WORKDIR /app
COPY poetry.lock pyproject.toml ./
RUN pip install poetry
RUN poetry install --no-root --no-interaction --no-cache
COPY . .