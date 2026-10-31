import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("BASETEN_API_KEY"),
    base_url="https://inference.baseten.co/v1",
)

models = client.models.list()

for model in models.data:
    print(model.id)