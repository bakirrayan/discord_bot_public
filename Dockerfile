# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /discordbot

COPY requirements.txt requirements.txt

RUN apt update && apt upgrade -y

RUN apt install nano -y

RUN apt install curl -y

RUN apt install procps -y

RUN pip3 install -r requirements.txt

COPY . .

COPY ./discord_bot/.env ./discord_bot

RUN chmod +x ./discord_bot/start.sh

CMD ["/bin/sh",  "./discord_bot/start.sh"]
