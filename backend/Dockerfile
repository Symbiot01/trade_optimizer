FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x /app/wait-for-it.sh

CMD ["sh", "-c", "./wait-for-it.sh warehouse_db:5432 -- uvicorn app.main:app --host 0.0.0.0 --port 8000"]
