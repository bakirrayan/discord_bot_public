#!/bin/bash

gunicorn --chdir ./discord_bot quiz_bot.wsgi &
python3 discord_bot/bot.py

