FROM python:3.12

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt requirements.txt

COPY . .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

RUN chmod 755 entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
