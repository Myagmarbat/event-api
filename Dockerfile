FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Mount the DO CA cert at runtime, e.g.:
#   docker run -v /path/to/ca-cert.crt:/run/secrets/do-ca-cert.crt \
#              -e DB_SSL_CA=/run/secrets/do-ca-cert.crt \
#              -e DATABASE_URL=postgresql://... ...
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]