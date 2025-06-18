# Use a stable version of Python
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy requirements first and install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy the rest of the code
COPY . .

# Expose the port (change if your app uses a different one)
EXPOSE 8000

# Start the app (modify if your main entry point is different)
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
