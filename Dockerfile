FROM python:3.6-alpine

RUN apk add --update \
    git \
    openssh

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

CMD ["python","app.py"]
