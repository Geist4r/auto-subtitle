FROM python:3.11-slim

RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements-api.txt .
RUN pip install --no-cache-dir -r requirements-api.txt

COPY auto_subtitle/ ./auto_subtitle/
COPY setup.py .

RUN mkdir -p /tmp/subtitle_api/outputs

EXPOSE 8080

CMD ["uvicorn", "auto_subtitle.api:app", "--host", "0.0.0.0", "--port", "8080"]
