# Step 1 - Start from official Python image
FROM python:3.11-slim

# Step 2 - Set working directory inside container
WORKDIR /app

# Step 3 - Copy requirements first (for caching)
COPY requirements.txt .

# Step 4 - Install all dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 5 - Copy your project files
COPY main.py .
COPY rag_pipeline.py .
COPY data/ ./data/

# Step 6 - Expose the port uvicorn runs on
EXPOSE 8000

# Step 7 - Command to run when container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]