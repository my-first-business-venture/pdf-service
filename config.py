import os
from dotenv import load_dotenv

load_dotenv()

FILE_PATH = os.getenv("FILE_PATH")
OPENAI_KEY = os.getenv("OPENAI_KEY")
LLM_MODEL = os.getenv("LLM_MODEL")

if not all([FILE_PATH, OPENAI_KEY, LLM_MODEL]):
    raise EnvironmentError("Missing one or more required environment variables.")
