FROM python:3.10.16-bullseye

WORKDIR /app

COPY pyproject.toml uv.lock as_flow.py as_local.py geoguessr_session.py signin.py /app/

RUN apt-get update &&  \
    apt install -y     \
          chromium         \
          chromium-driver  \
          chromium-sandbox \
          xvfb             \
          x11vnc \
          fluxbox \
          xterm \
          libffi-dev \
          git \
          ca-certificates

ENV CONTAINERISED="true"

RUN pip install uv && \
    uv export > requirements.txt && \
    pip install -r requirements.txt
