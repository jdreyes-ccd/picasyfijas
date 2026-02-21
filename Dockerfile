FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN playwright install --with-deps

#COPY src/ ./src/
#COPY tests/ ./tests/
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["python", "app/main.py"]
#CMD ["python", "-m", "pytest", "./tests", "-v"]
#CMD ["pytest", "--cov=src", "--cov-report=html", "--cov-report=xml"]