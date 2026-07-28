FROM python:3.14-slim

WORKDIR /app

ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libxcb1 && \
    rm -rf /var/lib/apt/lists/*

# Installing torch from the regular,PyPI gives you the GPU build with. This instl cmd grabs the CPU-only build instead. 
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install -r requirements.txt

COPY . .

WORKDIR /app/src/app

CMD ["fastapi", "run", "main.py"]
