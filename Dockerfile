FROM python:3.10-slim

# Install FFmpeg (required for audio playback)
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY .env .

# Copy directories
COPY src/ ./src/
COPY config/ ./config/
COPY songs/ ./songs/
COPY pics/ ./pics/

# Run the bot
CMD ["python", "main.py"]
