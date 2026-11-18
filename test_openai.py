
from dotenv import load_dotenv
from openai import OpenAI

# Load our API key
load_dotenv()

# Connect to OpenAI
client = OpenAI()

# Send a test request
response = client.responses.create(
    model="gpt-4.1-mini",
    input="Explain AI workflow automation in one sentence."
)

# Print the AI's response
print(response.output_text)
