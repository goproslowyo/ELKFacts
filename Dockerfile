# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code and elk facts
COPY elkfact_bot.py .
COPY elk.elkfacts.txt .
COPY oauth.py .

# Create a non-root user
RUN useradd -m botuser && chown -R botuser:botuser /app
USER botuser

# Run the bot
CMD ["python", "elkfact_bot.py"]
