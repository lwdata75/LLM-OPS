FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --upgrade pip

RUN pip install --no-cache-dir \
    "chainlit>=1.0.0" \
    "python-dotenv>=1.1.1" \
    "google-cloud-aiplatform>=1.120.0" \
    "google-cloud-storage>=2.19.0" \
    "google-cloud-bigquery>=3.38.0" \
    "requests>=2.31.0"

COPY src ./src
COPY .chainlit ./.chainlit
COPY chainlit.md ./

EXPOSE 8000

CMD ["chainlit", "run", "src/app/main.py", "--host", "0.0.0.0", "--port", "8000"]
