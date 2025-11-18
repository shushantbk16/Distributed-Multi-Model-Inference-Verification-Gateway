# Dockerfile
# Use a slim Python base image for small size
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Use --no-cache-dir to keep the image small (pro engineering practice)
RUN pip install --no-cache-dir -r requirements.txt

# Copy all the application files (main.py, llm_clients.py, etc.)
COPY . .

# Expose the default port for Uvicorn
EXPOSE 8000

# Command to run the Uvicorn web server
# The --reload flag is only for local testing. Remove it for final Render deployment.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]