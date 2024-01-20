FROM python:3.11.5-alpine

WORKDIR /app

COPY requirements.txt ./

RUN apk add --no-cache make gcc g++
RUN python -m pip install -U pip
RUN pip install --no-cache-dir -r requirements.txt
RUN apk del make gcc g++

COPY chsu_bot ./chsu_bot

CMD ["python", "./chsu_bot/main.py"]