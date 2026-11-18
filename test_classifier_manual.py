
from ai_classifier import analyze_ticket

result = analyze_ticket(
    subject="Duplicate subscription charge",
    message="I was charged twice and need a refund."
)

print(result)
