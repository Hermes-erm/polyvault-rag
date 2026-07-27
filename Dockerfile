FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 \
        libglib2.0-0 \
        libxcb1 && \
    rm -rf /var/lib/apt/lists/*

# Installing torch from the regular, This grabs the CPU-only build instead. PyPI gives you the GPU build with
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch torchvision && \
    pip install -r requirements.txt

COPY . .

WORKDIR /app/src/app

CMD ["fastapi", "run", "main.py"]
