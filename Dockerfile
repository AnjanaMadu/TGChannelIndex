FROM python:3.13-slim

# Install gcc and g++
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port 8080
EXPOSE 8080

# Remove gcc and g++ to reduce image size
RUN apt-get remove -y gcc g++ && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# Run the application
CMD ["python", "main.py"]