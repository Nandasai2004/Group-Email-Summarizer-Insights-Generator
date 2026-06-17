from google import genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

for m in client.models.list(config={"page_size": 50}):
    if "embed" in m.name.lower():
        print(m.name, m.supported_actions)
