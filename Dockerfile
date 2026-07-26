FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .

# RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir "fastapi[standard]"

RUN pip install -r requirements.txt
RUN pip install "fastapi[standard]"

COPY . .

WORKDIR /app/src/app

CMD ["fastapi", "run", "main.py"]
