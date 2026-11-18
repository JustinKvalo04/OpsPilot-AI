
import os

from ai_classifier import analyze_ticket
from database import get_live_ai_call_count

before = get_live_ai_call_count()

# Temporarily simulate live mode with paid calls disabled
os.environ["AI_MODE"] = "live"
os.environ["ENABLE_PAID_AI"] = "false"

try:
    analyze_ticket(
        "Refund request",
        "I was charged twice and need a refund."
    )
except RuntimeError as error:
    print("PASS - Live mode blocked:", error)
else:
    raise AssertionError("Live mode was not blocked!")

after = get_live_ai_call_count()

assert before == after
print("PASS - No live request reservations added")
print("Live AI calls:", after)
