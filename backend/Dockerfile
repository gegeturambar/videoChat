FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y \
    curl \
    postgresql-client \
    ca-certificates \
    ffmpeg \
    openssl \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/* 
    
WORKDIR /app

# Mise à jour des certificats
RUN update-ca-certificates

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade yt-dlp certifi

COPY . .

ENV PYTHONPATH=/app
# Activer la vérification SSL pour Python
ENV PYTHONHTTPSVERIFY=1
ENV SSL_CERT_FILE=/etc/ssl/certs/ca-certificates.crt
ENV REQUESTS_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt
ENV CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt

EXPOSE 8000

# Rendre le script de démarrage exécutable
RUN chmod +x start.sh

CMD ["./start.sh"] 