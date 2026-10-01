# 1. Start with a lightweight Python base image
FROM python:3.12-slim

# 2. Install 'uv' for lightning-fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set the working directory inside the container
WORKDIR /app

# 4. Copy dependency files first (Docker caches this layer!)
COPY pyproject.toml uv.lock ./

RUN mkdir -p src/brokerlite_portfolio && touch src/brokerlite_portfolio/__init__.py
RUN touch README.md

# 5. Install dependencies (no dev tools needed in production)
RUN uv sync --frozen --no-dev

# 6. Copy the rest of your application code
COPY . .

# 7. Expose the port the service runs on
EXPOSE 8002

# 8. The command to run when the container starts
# CRITICAL: We use 0.0.0.0 instead of 127.0.0.1 so Docker can route traffic to it!
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]