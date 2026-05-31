FROM python:3.13-alpine

WORKDIR /app

ENV TZ=Asia/Shanghai

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENTRYPOINT ["python", "app.py"]
