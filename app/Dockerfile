FROM python:3.8.3-alpine

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/app

RUN mkdir -p ./mediafiles
RUN mkdir -p ./staticfiles/admin

RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev ffmpeg

RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]