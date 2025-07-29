FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml .
COPY setup.py .

# Install Python dependencies
RUN pip install -e .

# Copy source code
COPY src/ ./src/
COPY .env .env

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit app
CMD ["streamlit", "run", "src/interfaces/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
