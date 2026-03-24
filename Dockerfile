FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Install holehe from local source
RUN pip install --no-cache-dir -e .

# Expose API port
EXPOSE 8000

# Environment defaults (override at runtime)
ENV HOST=0.0.0.0 \
    PORT=8000 \
    DEBUG=false \
    TIMEOUT=15 \
    API_KEY=""

CMD ["python", "api.py"]
