FROM mambaorg/micromamba:1.5-jammy

WORKDIR /app

COPY environment.yml .

RUN micromamba install --yes \
  --name base \
  -f environment.yml \
  && micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1

COPY . .

ENTRYPOINT ["micromamba", "run", "-n", "base", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
