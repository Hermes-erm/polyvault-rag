FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libxcb1 && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir "fastapi[standard]"
RUN pip install --no-cache-dir "docling[rapidocr]"

COPY . .

WORKDIR /app/src/app

CMD ["fastapi", "run", "main.py"]
