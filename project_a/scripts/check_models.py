import os, sys
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

for name in sys.argv[1:]:
    try:
        r = client.models.generate_content(model=name, contents="Say ok")
        print(f"WORKS    {name}: {r.text.strip()[:20]}")
    except Exception as e:
        print(f"FAILS    {name}: {str(e)[:100]}")