
from ai_classifier import analyze_ticket_with_openai
from database import get_live_ai_call_count

before = get_live_ai_call_count()

try:
    analyze_ticket_with_openai(
        "Refund request",
        "I was charged twice and need a refund."
    )
except RuntimeError as error:
    print("Safety check:", error)

after = get_live_ai_call_count()

print("Live AI calls before:", before)
print("Live AI calls after:", after)

assert before == after
print("PASS - Paid requests are blocked")
