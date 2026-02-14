FROM python:3.10-slim

WORKDIR /app

# Copy deps first (cache-friendly)
COPY requirements.txt .

# Faster + more reliable pip install
RUN pip install --no-cache-dir \
    --default-timeout=100 \
    --retries=5 \
    -i https://pypi.org/simple \
    -r requirements.txt

# Copy app code
COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
