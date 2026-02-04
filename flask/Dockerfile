FROM python:3.11.6-alpine3.18

WORKDIR /app

ENV TZ=Asia/Taipei

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

RUN sed -i 's/dl-cdn.alpinelinux.org/ftp.jaist.ac.jp/g' /etc/apk/repositories && \
    apk add --no-cache --virtual .build-deps gcc libc-dev linux-headers python3-dev && \
    pip install uwsgi && \
    apk del .build-deps

COPY . .

EXPOSE 8080

CMD ["uwsgi", "--ini", "uwsgi.ini"]
# CMD ["python", "main.py"]