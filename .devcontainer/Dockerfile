FROM mcr.microsoft.com/devcontainers/python:2-3.14-trixie

# Install system ODBC libs required by pyodbc and Azure SQL connectivity.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    gnupg \
    odbcinst \
    python3-dev \
    unixodbc \
    unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*
