FROM python:3.11.6-alpine3.18

WORKDIR /app

ENV TZ=Asia/Taipei

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "-c", "gunicorn_config.py", "main:app"]