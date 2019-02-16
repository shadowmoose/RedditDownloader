FROM python:3.7-slim

WORKDIR ./rmd/

ADD redditdownloader/classes ./classes
ADD redditdownloader/tests ./tests
ADD redditdownloader/web ./web
ADD docs ./docs
ADD main.py ./
ADD requirements.txt ./



RUN mkdir ./settings/

RUN pip install -r ./requirements.txt

ENTRYPOINT [ "python", "-u", "./main.py", "--settings", "./settings/settings.json"]
