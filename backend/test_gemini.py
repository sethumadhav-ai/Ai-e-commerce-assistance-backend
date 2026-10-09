import os
from dotenv import load_dotenv
from google import genai

# Load the .env file
load_dotenv()

# Get the API key from .env
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: GEMINI_API_KEY was not found.")
    exit()

# Connect to Gemini
client = genai.Client(api_key=api_key)

# Send a test request
response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Say hello and tell me you are working."
)

print("\nGemini response:")
print(response.text)