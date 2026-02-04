FROM python:3.11.6-alpine3.18

WORKDIR /app
ENV TZ=Asia/Taipei

# 先裝系統 uwsgi + python3 plugin（已編譯好）
RUN apk add --no-cache uwsgi uwsgi-python3

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .
EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi.ini"]

# CMD ["python", "main.py"]