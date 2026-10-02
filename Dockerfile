FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
RUN useradd --create-home api
USER api
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "src:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
