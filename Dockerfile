FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies (needed for chroma and fpdf)
RUN apt-get update && apt-get install -y \
    build-essential \
    nginx \
    gettext-base \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make the start script executable
RUN chmod +x start.sh

# Expose the ports for FastAPI and Streamlit
EXPOSE 8000
EXPOSE 8501

# Command to run both servers
CMD ["./start.sh"]
