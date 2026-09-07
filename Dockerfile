FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY assistant ./assistant
COPY grocy ./grocy
COPY notifications ./notifications
COPY config ./config
COPY templates ./templates
COPY app.py .

CMD ["python", "-u", "app.py"]