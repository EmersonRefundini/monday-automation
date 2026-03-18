FROM mcr.microsoft.com/playwright/python:v1.58.0-noble

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

CMD ["gunicorn", "-b", "0.0.0.0:8080", "webhook:app", "--workers", "1", "--threads", "4", "--timeout", "120"]