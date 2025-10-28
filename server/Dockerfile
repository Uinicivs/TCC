# --- Estágio 1: Imagem Base com Dependências ---
# Usamos uma imagem slim do Python 3.12 para manter o tamanho final pequeno.
FROM python:3.12-slim AS base

# Define variáveis de ambiente para otimizar o Python no Docker.
# PYTHONDONTWRITEBYTECODE: Impede o Python de criar arquivos .pyc.
# PYTHONUNBUFFERED: Garante que os logs sejam enviados diretamente para o terminal.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências do sistema para TLS/SSL e build tools
RUN apt-get update && apt-get install -y \
    libssl-dev \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instala o 'uv', o gerenciador de pacotes que você está usando.
RUN pip install uv

# Define o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Copia os arquivos de dependência para o contêiner.
# Fazer isso antes de copiar o resto do código aproveita o cache do Docker.
COPY pyproject.toml uv.lock ./

# Instala as dependências de produção usando o uv.lock.
# A flag --no-dev garante que pacotes de teste (como pytest) não sejam instalados.
RUN uv sync --no-dev


# --- Estágio 2: Imagem Final da Aplicação ---
# Começamos a partir da imagem base que já tem as dependências instaladas.
FROM base AS final

# Define o diretório de trabalho (herdado da base, mas é bom ser explícito).
WORKDIR /app

# Define o PYTHONPATH para que os imports a partir de 'src' funcionem corretamente.
# Isso replica a configuração do seu debugger.
ENV PYTHONPATH=/app

ARG API_PORT=8000

# Copia o código fonte da sua aplicação para o contêiner.
COPY src/ ./src/
COPY grammar.lark ./grammar.lark

# Expõe a porta em que o FastAPI/uvicorn irá rodar.
EXPOSE ${API_PORT}

# Comando para iniciar a aplicação quando o contêiner for executado.
# --host 0.0.0.0 é essencial para que a aplicação seja acessível de fora do contêiner.
# O comando é equivalente a 'uv run --host 0.0.0.0 --port 8000 -m src.main'.
CMD ["uv", "run", "-m", "src.main"]
