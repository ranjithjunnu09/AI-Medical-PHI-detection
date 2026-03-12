FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --default-timeout=100 -i https://pypi.org/simple -r requirements.txt

RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    poppler-utils

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]