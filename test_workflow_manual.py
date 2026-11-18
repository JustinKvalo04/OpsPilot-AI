
from workflow_engine import route_ticket

analysis = {
    "category": "billing",
    "priority": "high",
    "department": "finance",
    "requires_human_review": True
}

result = route_ticket(analysis)

print(result)
