import os
from openai import OpenAI
from dotenv import load_dotenv
import time


start_time = time.time()

load_dotenv()

client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY')
)

completion = client.chat.completions.create(
  model="gpt-4",
  messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello!"}
  ]
)