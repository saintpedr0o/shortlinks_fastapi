FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src
COPY alembic.ini .
COPY alembic/ ./alembic/
EXPOSE 8000
CMD ["sh", "-c", "if [ \"$DEBUG\" = \"True\" ]; then uvicorn src.main:app --host ${HOST} --port ${PORT} --reload; else uvicorn src.main:app --host ${HOST} --port ${PORT}; fi"]

