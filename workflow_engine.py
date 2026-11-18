
def route_ticket(analysis: dict):
    # Get the classification results
    department = analysis["department"]
    priority = analysis["priority"]
    requires_review = analysis["requires_human_review"]

    # Determine the next workflow step
    if requires_review:
        status = "pending_approval"
        action = "Send ticket for human approval"
    else:
        status = "in_progress"
        action = f"Route ticket to {department}"

    return {
        "assigned_department": department,
        "priority": priority,
        "status": status,
        "next_action": action
    }
