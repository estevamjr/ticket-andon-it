# Usando uma imagem Python oficial leve
FROM python:3.10-slim

# Definir diretório de trabalho
WORKDIR /app

# Váriaveis de ambiente para não gerar .pyc e não usar buffer no log
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar dependências do sistema necessárias para compilar pacotes (como psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar os requirements e instalar dependências
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar todo o código do projeto para o container
COPY . .

# Expor a porta 5000
EXPOSE 5000

# Comando para rodar a aplicação via Gunicorn (recomendado para produção)
# Supondo que a instância do Flask (app) esteja no arquivo app.py ou wsgi.py
CMD ["python", "app.py"]