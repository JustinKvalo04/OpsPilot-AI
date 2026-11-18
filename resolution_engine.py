
# resolution_engine.py
# Policy-grounded resolution recommendations for OpsPilot AI.
# This module does not call an external AI service.

from typing import Any


def _policy_text(policy: dict) -> str:
    return " ".join(
        str(policy.get(key, ""))
        for key in ("title", "category", "content")
    ).lower()


def generate_resolution(
    analysis: dict[str, Any],
    workflow: dict[str, Any],
    relevant_policies: list[dict[str, Any]],
) -> dict[str, Any]:

    category = str(
        analysis.get("category", "general_inquiry")
    ).lower()

    department = str(
        workflow.get(
            "assigned_department",
            analysis.get("assigned_department", "customer_support")
        )
    )

    priority = str(
        workflow.get(
            "priority",
            analysis.get("priority", "low")
        )
    )

    requires_approval = (
        bool(analysis.get("requires_human_review", False))
        or workflow.get("status") == "pending_approval"
    )

    policy_ids = [
        str(policy["id"])
        for policy in relevant_policies
        if policy.get("id")
    ]

    policy_text = " ".join(
        _policy_text(policy)
        for policy in relevant_policies
    )

    steps = []
    rationale = []

    if category == "billing":
        title = "Review and resolve billing request"

        steps = [
            "Verify the customer's billing or payment details.",
            "Review the applicable billing and refund policy.",
            "Determine whether the requested adjustment is eligible.",
            "Send the case to Finance for review.",
            "Communicate the decision to the customer."
        ]

        rationale.append(
            "Billing issues may involve financial adjustments "
            "and should be handled by the Finance team."
        )

    elif category == "technical_support":
        title = "Investigate and resolve technical issue"

        steps = [
            "Confirm the reported error and affected service.",
            "Collect relevant error messages and reproduction steps.",
            "Review the technical support policy.",
            "Investigate the cause or escalate to IT.",
            "Verify the fix before updating the customer."
        ]

        rationale.append(
            "Technical issues require troubleshooting and "
            "verification before the case can be resolved."
        )

    elif category == "account_management":
        title = "Resolve account access or subscription issue"

        steps = [
            "Verify the customer's identity using approved procedures.",
            "Review the account management policy.",
            "Investigate the reported account issue.",
            "Apply only authorized account changes.",
            "Confirm the outcome with the customer."
        ]

        rationale.append(
            "Account-related requests require identity "
            "verification and appropriate access controls."
        )

    else:
        title = "Review and respond to customer inquiry"

        steps = [
            "Review the customer's request.",
            "Identify the relevant company guidance.",
            "Determine whether additional information is needed.",
            "Prepare a response or escalate to the assigned team.",
            "Record the outcome."
        ]

        rationale.append(
            "General inquiries should be reviewed and "
            "routed to the appropriate support team."
        )

    if relevant_policies:
        rationale.append(
            "Relevant company policies were retrieved "
            "to support the recommendation."
        )
    else:
        rationale.append(
            "No matching policy was retrieved. "
            "A human should verify the applicable guidance."
        )

    if "refund" in policy_text and category == "billing":
        rationale.append(
            "Retrieved policy guidance discusses refunds "
            "or billing adjustments."
        )

    if requires_approval:
        steps.insert(
            -1,
            "Obtain human approval before performing "
            "any restricted or sensitive action."
        )

        rationale.append(
            "The existing workflow requires human review."
        )

    if priority == "high":
        rationale.append(
            "The ticket has been classified as high priority."
        )

    return {
        "recommendation_title": title,
        "recommended_department": department,
        "priority": priority,
        "requires_human_approval": requires_approval,
        "recommended_steps": steps,
        "reasoning": " ".join(rationale),
        "referenced_policies": policy_ids,
        "policy_match_found": bool(relevant_policies),
        "recommendation_type": "rule_based",
        "execution_status": "recommendation_only",
        "disclaimer": (
            "This is a suggested workflow, not an executed "
            "resolution. Policy eligibility and approvals "
            "must be verified by an authorized employee."
        )
    }
