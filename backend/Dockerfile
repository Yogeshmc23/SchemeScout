FROM python:3.11-slim
WORKDIR /app
COPY requirements.lock ./requirements.lock
RUN pip install --no-cache-dir -r requirements.lock
COPY pyproject.toml ./
COPY app ./app
RUN pip install --no-deps . && useradd --create-home radar
USER radar
EXPOSE 8000
CMD ["sh", "-c", "python -m app.db && uvicorn app.main:app --host 0.0.0.0 --port 8000 --no-access-log"]
