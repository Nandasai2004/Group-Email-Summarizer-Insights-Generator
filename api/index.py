from fastapi import FastAPI
from backend.main import app as backend_app

app = FastAPI(title="GES Webhook API (Vercel Zero-Config)")
app.mount("/", backend_app)
