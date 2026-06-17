from fastapi import FastAPI
from backend.main import app as backend_app

# This explicitly instantiates FastAPI to satisfy Vercel's AST auto-scanner
app = FastAPI(title="GES Webhook API (Vercel Root Entrypoint)")

# We mount your actual backend application here so all routes work exactly the same
app.mount("/", backend_app)
