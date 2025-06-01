FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables early
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONOPTIMIZE=1
ENV DJANGO_SETTINGS_MODULE=image_colorizer.settings
ENV PORT=8000

# Install Python dependencies with optimizations
COPY requirements.txt .
RUN pip install --no-cache-dir --compile -r requirements.txt \
    && pip cache purge \
    && find /usr/local -type d -name __pycache__ -exec rm -r {} + || true

# Copy project files
COPY . .

# Collect static files (only if needed for production)
RUN python manage.py collectstatic --noinput --clear

# Run migrations during deployment, not build
# RUN python manage.py migrate

# Create a non-root user for security
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Expose the port
EXPOSE 8000

# Start Gunicorn with memory-optimized settings
CMD python manage.py migrate && \
    gunicorn image_colorizer.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers=1 \
    --threads=2 \
    --timeout=120 \
    --max-requests=1000 \
    --max-requests-jitter=100 \
    --preload \
    --worker-class=sync
