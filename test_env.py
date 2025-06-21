import os
from dotenv import load_dotenv

load_dotenv()
print("BFL_API_KEY:", os.getenv("BFL_API_KEY"))