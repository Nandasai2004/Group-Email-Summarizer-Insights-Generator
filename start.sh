#!/bin/bash

# Default port to 10000 if not provided by the cloud platform
export PORT=${PORT:-10000}

# Generate nginx config with the correct port
envsubst '${PORT}' < nginx.conf.template > /etc/nginx/nginx.conf

# Start the FastAPI backend webhook server in the background (internal port 8000)
echo "Starting FastAPI Backend Webhook Server..."
uvicorn backend.main:app --host 127.0.0.1 --port 8000 &

# Start the Streamlit Dashboard in the background (internal port 8501)
echo "Starting Streamlit Dashboard..."
streamlit run frontend/app.py --server.port 8501 --server.address 127.0.0.1 &

# Start NGINX in the foreground to route external traffic to both internal servers
echo "Starting NGINX reverse proxy on port $PORT..."
nginx -g 'daemon off;'
