# build : 
#    
#    docker compose build
#
# run :
#    
#    docker compose up        
#
# entrer dans le container :
#    
#    docker compose run --rm --entrypoint bash app    
#

# Stage 1 : base
FROM python:3.13-slim AS builder

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_SYSTEM_PYTHON=1

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev

RUN ls -la /app/.venv/bin/

# Stage 2: Runtime
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

COPY --from=builder /app/.venv .venv
COPY . .

EXPOSE 8377

CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8377"]
