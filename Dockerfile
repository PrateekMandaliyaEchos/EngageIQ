# Multi-stage build for frontend + backend
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/

# Copy scripts
COPY scripts/ ./scripts/
COPY config.yaml ./

# Copy built frontend
COPY --from=frontend-build /app/frontend/dist ./static

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Create startup script
RUN echo '#!/bin/bash\n\
echo "🚀 Starting EngageIQ..."\n\
echo "📊 Initializing data..."\n\
python scripts/init_data.py\n\
echo "🌐 Starting web server..."\n\
python src/api/run_server.py' > /app/start.sh && chmod +x /app/start.sh

# Run the application
CMD ["/app/start.sh"]
