# ===============================
# 1️⃣ Base leve e moderna
# ===============================
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

# Copia binários do uv diretamente da imagem oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Instala pacotes essenciais e limpa o cache
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# ===============================
# 2️⃣ Instala dependências
# ===============================
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-cache --no-dev

# ===============================
# 3️⃣ Copia somente o código da aplicação
# ===============================
COPY src ./src
COPY grammar.lark ./

# ===============================
# 4️⃣ Ambiente e segurança
# ===============================
RUN useradd -m appuser
USER appuser

EXPOSE 10000

# ===============================
# 5️⃣ Comando padrão (produção)
# ===============================
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "10000"]
