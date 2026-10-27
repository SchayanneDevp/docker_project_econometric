
FROM condaforge/miniforge3:latest

WORKDIR /proyecto

# Instalar Quarto como programa del sistema
ARG QUARTO_VERSION=1.11.5

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tar \
    && mkdir -p /opt/quarto/${QUARTO_VERSION} \
    && curl -fsSL \
       "https://github.com/quarto-dev/quarto-cli/releases/download/v${QUARTO_VERSION}/quarto-${QUARTO_VERSION}-linux-amd64.tar.gz" \
       -o /tmp/quarto.tar.gz \
    && tar -xzf /tmp/quarto.tar.gz \
       -C /opt/quarto/${QUARTO_VERSION} \
       --strip-components=1 \
    && ln -s /opt/quarto/${QUARTO_VERSION}/bin/quarto /usr/local/bin/quarto \
    && rm /tmp/quarto.tar.gz \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY environment.yml .

RUN conda env create -f environment.yml \
    && conda clean --all -y

ENV PATH=/opt/conda/envs/analisis-pasajeros/bin:$PATH
ENV PYTHONUNBUFFERED=1

COPY . .

CMD ["snakemake", "--cores", "2"]
