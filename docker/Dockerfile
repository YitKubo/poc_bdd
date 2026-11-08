FROM python:3.12-slim

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JAVA_TOOL_OPTIONS=-Djava.awt.headless=true

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential cmake make git clang-format \
        default-jre-headless libharfbuzz0b libfreetype6 fontconfig curl fonts-ipafont-gothic \
    && rm -rf /var/lib/apt/lists/*

# PlantUML: apt 版は古く analog（物理値の波形）が使えないため、公式 jar を固定バージョンで入れる
ARG PLANTUML_VERSION=1.2026.9
ARG PLANTUML_SHA1=c2598e381d3ea0f2e46e56c654fc99ac113193a8
RUN curl -fsSL -o /opt/plantuml.jar \
        https://repo1.maven.org/maven2/net/sourceforge/plantuml/plantuml/${PLANTUML_VERSION}/plantuml-${PLANTUML_VERSION}.jar \
    && echo "${PLANTUML_SHA1}  /opt/plantuml.jar" | sha1sum -c - \
    && printf '#!/bin/sh\nexec java -jar /opt/plantuml.jar "$@"\n' > /usr/local/bin/plantuml \
    && chmod +x /usr/local/bin/plantuml

COPY requirements-dev.txt /tmp/requirements-dev.txt
RUN pip install --no-cache-dir -r /tmp/requirements-dev.txt

# reformat-gherkin は gherkin-official==24 に固定されていて pytest-bdd と衝突するため、別 venv に隔離する
RUN python -m venv /opt/gherkin-fmt \
    && /opt/gherkin-fmt/bin/pip install --no-cache-dir reformat-gherkin \
    && ln -s /opt/gherkin-fmt/bin/reformat-gherkin /usr/local/bin/reformat-gherkin

RUN useradd --create-home --uid 1000 --shell /bin/bash dev
USER dev
WORKDIR /work
