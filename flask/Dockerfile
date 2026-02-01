FROM python:3.11.6-slim

WORKDIR /app

ENV TZ=Asia/Taipei

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN pip install --no-cache-dir uwsgi

COPY . .

EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi.ini"]