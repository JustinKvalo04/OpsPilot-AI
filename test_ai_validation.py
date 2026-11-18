
from pydantic import ValidationError
from ai_classifier import AIClassification

valid_response = {
    "category": "billing",
    "priority": "high",
    "department": "finance",
    "summary": "Customer requests a refund.",
    "requires_human_review": True
}

invalid_response = {
    "category": "billing",
    "priority": "extreme",
    "department": "unknown",
    "summary": "Refund request",
    "requires_human_review": True
}

# Test a valid response
validated = AIClassification.model_validate(valid_response)
print("PASS - Valid classification accepted")

# Test an invalid response
try:
    AIClassification.model_validate(invalid_response)
    raise AssertionError("Invalid response was accepted!")
except ValidationError:
    print("PASS - Invalid classification rejected")

print("AI response validation is working!")
