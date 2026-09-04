FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir requests flask

COPY acw_s2.py .
COPY templates ./templates

CMD ["python", "-u", "acw_s2.py"]
