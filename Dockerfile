FROM python:slim-bullseye

WORKDIR /app

COPY as_flow.py as_local.py geoguessr_session.py signin.py requirements.txt /app/

RUN pip install -r requirements.txt
