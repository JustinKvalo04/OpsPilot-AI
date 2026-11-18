
import os

# Force free mock mode for this test
os.environ["AI_MODE"] = "mock"
os.environ["ENABLE_PAID_AI"] = "false"

from fastapi.testclient import TestClient
from main import app
from knowledge_base import search_knowledge_base
from database import get_live_ai_call_count

client = TestClient(app)

before = get_live_ai_call_count()

print("\n=== OpsPilot Knowledge Base Tests ===")

# Test 1: Policy retrieval
results = search_knowledge_base(
    "I was charged twice and need a refund"
)

assert len(results) > 0
assert results[0]["id"] == "POL-001"
print("PASS - Refund policy retrieved")


# Test 2: Knowledge search endpoint
response = client.get(
    "/knowledge/search",
    params={"query": "password reset account"}
)

assert response.status_code == 200
assert response.json()["results"][0]["id"] == "POL-002"
print("PASS - Knowledge search API working")


# Test 3: Full ticket workflow
response = client.post(
    "/tickets",
    json={
        "subject": "Duplicate billing charge",
        "message": "I was charged twice and need a refund."
    }
)

assert response.status_code == 201
ticket_id = response.json()["id"]

response = client.post(
    f"/tickets/{ticket_id}/process"
)

assert response.status_code == 200

data = response.json()

assert data["analysis"]["category"] == "billing"
assert data["workflow"]["status"] == "pending_approval"
assert data["relevant_policies"][0]["id"] == "POL-001"

print("PASS - Ticket processed with relevant policy")


# Test 4: Human approval
response = client.post(
    f"/tickets/{ticket_id}/approve",
    json={
        "approved": True,
        "reviewer": "Test Manager",
        "reason": "Verified duplicate payment"
    }
)

assert response.status_code == 200
assert response.json()["decision"] == "approved"

print("PASS - Human approval working")


# Test 5: Audit history
response = client.get(
    f"/tickets/{ticket_id}/history"
)

assert response.status_code == 200
assert len(response.json()["history"]) == 3

print("PASS - Audit logging working")


# Test 6: No paid requests
after = get_live_ai_call_count()

assert before == after

print("PASS - No paid OpenAI requests made")
print("\nALL KNOWLEDGE BASE TESTS PASSED!")
