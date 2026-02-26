# ExamOps Orchestrator — Azure Functions container image
# Extends the official Azure Functions Python 3.11 base image.
# Build: docker build -t examops-orchestrator .
# Run locally: docker run -p 7071:80 --env-file .env examops-orchestrator

FROM mcr.microsoft.com/azure-functions/python:4-python3.11

# Working directory expected by the Azure Functions runtime
WORKDIR /home/site/wwwroot

# Install Python dependencies first (layer-cached unless requirements change)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/
COPY tests/ ./tests/

# Azure Functions runtime discovers functions via the host.json at the root
COPY host.json .

# Environment variables are injected at runtime via Azure App Settings / --env-file.
# Do NOT bake secrets into the image.

# The Azure Functions runtime listens on port 80 inside the container.
EXPOSE 80
