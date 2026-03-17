FROM python:3.11-slim

LABEL maintainer="OpenClaw"
LABEL description="OpenClaw Pipeline Monitor - Kanban-style task flow dashboard"

# Set working directory
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors

# Copy application
COPY server.py .

# Expose port
EXPOSE 5050

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5050/health || exit 1

# Run the application
CMD ["python3", "-u", "server.py"]