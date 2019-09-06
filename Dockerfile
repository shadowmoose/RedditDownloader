FROM python:3.7-slim

ADD redditdownloader ./redditdownloader

RUN mkdir ./settings/

RUN pip install -r ./redditdownloader/requirements.txt

ENTRYPOINT [ "python", "-u", "./redditdownloader/main.py", "--settings", "./settings/settings.json"]
