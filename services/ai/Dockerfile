FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./

# Create dummy files to satisfy uv's strict packaging checks
RUN mkdir -p src/brokerlite_ai && touch src/brokerlite_ai/__init__.py
RUN touch README.md

RUN uv sync --frozen --no-dev

COPY . .
EXPOSE 8003
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8003"]