# 1. Start with a lightweight Python base image
FROM python:3.12-slim

# 2. Install 'uv'
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Set the working directory
WORKDIR /app

# 4. Copy dependency files
COPY pyproject.toml uv.lock ./

RUN mkdir -p src/brokerlite_notifications && touch src/brokerlite_notifications/__init__.py
RUN touch README.md

# 5. Install dependencies
RUN uv sync --frozen --no-dev

# 6. Copy application code
COPY . .

# NO EXPOSE NEEDED! This service doesn't accept HTTP requests.

# 7. Run the script
CMD ["uv", "run", "python", "app/main.py"]