FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && playwright install --with-deps

# Copy only required project files to reduce attack surface and avoid leaking local artifacts.
COPY app/ ./app/
COPY src/ ./src/
COPY tests/ ./tests/
COPY e2e/ ./e2e/
COPY pytest.ini ./
COPY docker-compose.yml ./
COPY sonar-project.properties ./

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
#CMD ["python", "app/main.py"]
#CMD ["python", "-m", "pytest", "./tests", "-v"]
#CMD ["pytest", "--cov=src", "--cov-report=html", "--cov-report=xml"]