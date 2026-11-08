FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_TOOL_OPTIONS=-Djava.awt.headless=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential cmake make git clang-format \
        plantuml fonts-ipafont-gothic \
    && rm -rf /var/lib/apt/lists/*

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt

# reformat-gherkin は gherkin-official==24 に固定されていて pytest-bdd と衝突するため、別 venv に隔離する
RUN python -m venv /opt/gherkin-fmt \
    && /opt/gherkin-fmt/bin/pip install --no-cache-dir reformat-gherkin \
    && ln -s /opt/gherkin-fmt/bin/reformat-gherkin /usr/local/bin/reformat-gherkin

RUN useradd --create-home --uid 1000 --shell /bin/bash dev
USER dev
WORKDIR /work
