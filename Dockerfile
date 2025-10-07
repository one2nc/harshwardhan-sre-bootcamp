# syntax=docker/dockerfile:1.7-labs

FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN opentelemetry-bootstrap -a install

COPY --exclude=.env --exclude=instance . .

RUN chmod +x entrypoint.sh

CMD ["/bin/sh","-c","/app/entrypoint.sh"]