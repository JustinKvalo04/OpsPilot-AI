
# response_generator.py
# Deterministic customer response drafting.
# No external AI calls and no automatic sending.

from typing import Any


def generate_customer_response(
    ticket: Any,
    analysis: dict,
    recommendation: dict,
    policies: list[dict],
) -> dict:

    category = str(
        analysis.get("category", "general_inquiry")
    ).lower()

    approval_required = bool(
        recommendation.get("requires_human_approval")
    )

    policy_ids = [
        str(policy["id"])
        for policy in policies
        if policy.get("id")
    ]

    if category == "billing":
        subject = "Re: Your billing inquiry"

        body = (
            "Hello,\n\n"
            "Thank you for contacting us about your billing "
            "concern. We understand that you would like "
            "assistance with this issue.\n\n"
            "Our team will review the details of your request "
            "and the applicable billing policies. "
            "Any refund or billing adjustment will be "
            "subject to verification and approval.\n\n"
            "We will follow up once the review is complete.\n\n"
            "Best regards,\n"
            "Customer Support Team"
        )

    elif category == "technical_support":
        subject = "Re: Your technical support request"

        body = (
            "Hello,\n\n"
            "Thank you for reporting this technical issue. "
            "We understand the inconvenience it may cause.\n\n"
            "Our technical support team will review the "
            "information provided and investigate the issue. "
            "We may contact you if additional details "
            "are needed.\n\n"
            "We will provide an update when more "
            "information is available.\n\n"
            "Best regards,\n"
            "Technical Support Team"
        )

    elif category == "account_management":
        subject = "Re: Your account support request"

        body = (
            "Hello,\n\n"
            "Thank you for contacting us about your account.\n\n"
            "Our support team will review your request "
            "and follow the appropriate account security "
            "and verification procedures before making "
            "any changes.\n\n"
            "We will follow up with the next steps "
            "as soon as possible.\n\n"
            "Best regards,\n"
            "Customer Support Team"
        )

    else:
        subject = "Re: Your support inquiry"

        body = (
            "Hello,\n\n"
            "Thank you for reaching out to our support team.\n\n"
            "We have received your inquiry and will review "
            "the details to determine the appropriate "
            "next steps. If additional information is "
            "needed, our team will contact you.\n\n"
            "Thank you for your patience.\n\n"
            "Best regards,\n"
            "Customer Support Team"
        )

    return {
        "ticket_id": ticket.id,
        "subject": subject,
        "body": body,
        "category": category,
        "referenced_policies": policy_ids,
        "requires_human_approval": approval_required,
        "status": "draft",
        "generation_method": "rule_based_template",
        "automatically_sent": False,
        "review_notes": (
            "Verify the draft against the original ticket "
            "and applicable company policies before use. "
            "No policy-specific eligibility determination "
            "has been made."
        ),
    }
