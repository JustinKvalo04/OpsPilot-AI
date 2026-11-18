
import os
from dotenv import load_dotenv

from ai_classifier import analyze_ticket_with_openai
from database import get_live_ai_call_count

load_dotenv()

print("=== OpsPilot First Live AI Test ===")

if os.getenv("ENABLE_PAID_AI", "false").lower() != "true":
    print("BLOCKED: Paid AI requests are disabled.")
    print("No API request was made.")
    raise SystemExit(0)

before = get_live_ai_call_count()
print("Live requests before:", before)

result = analyze_ticket_with_openai(
    subject="Duplicate subscription charge",
    message="I was charged twice for my monthly subscription and need a refund."
)

print("\nAI Classification:")
print(result)

after = get_live_ai_call_count()
print("\nLive requests after:", after)
