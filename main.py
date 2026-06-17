# Root-level entrypoint for cloud deployment platforms (Render, Vercel, Railway, etc.)
# This redirects the default 'fastapi run' command to your backend application.

from backend.main import app
