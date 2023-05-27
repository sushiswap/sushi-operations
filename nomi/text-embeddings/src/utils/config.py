from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

OPEN_API_KEY = os.environ["OPENAI_API_KEY"]
