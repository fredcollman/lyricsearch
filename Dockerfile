FROM python:3.7-slim

WORKDIR /app
COPY pyproject.toml setup.cfg /app/
COPY src /app/src
RUN pip install ".[dev]"

ENTRYPOINT ["python", "-m", "lyricsearch"]
