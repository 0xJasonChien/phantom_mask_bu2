FROM python:3.12-slim

RUN mkdir /code && \
    apt update && \
    apt install -y --no-install-recommends nano libpq-dev && \
    apt clean && \
    pip install --upgrade pip && \
    pip install uv && \
    adduser phantom-mask

USER phantom-mask
ENV PYTHONUNBUFFERED=1

WORKDIR /home/phantom-mask/src/
COPY uv.lock pyproject.toml ./
RUN uv sync

COPY --chown=phantom-mask:phantom-mask ./src/ ./
COPY --chown=phantom-mask:phantom-mask ./data /home/phantom-mask/data

CMD ["sh", "backend-entrypoint.sh"]
