# 1. Use an official lightweight Python runtime as a parent image
FROM python:3.10-slim

# 2. Set system environment variables to optimize Python inside the container
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Set the working directory inside the container space
WORKDIR /workspace

# 4. Install system dependencies required for compiling drivers (like psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Sauberer Import aus dem Hauptverzeichnis (Kontext ist nun wieder `.`)
COPY requirements.txt .

# 6. Upgrade pip and install all Python dependencies cleanly
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 7. Kopiert das gesamte Projekt sauber in den Container
COPY . .

# 8. Expose the default port FastAPI runs on
EXPOSE 8000
