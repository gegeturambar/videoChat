FROM ghcr.io/chroma-core/chroma:0.6.3

# Installation de curl
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* 