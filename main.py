
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from uuid import uuid4
from typing import Literal

from fastapi import Depends, Header

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai_classifier import analyze_ticket
from workflow_engine import route_ticket
from knowledge_base import (
    search_knowledge_base,
    retrieve_ticket_context,
)
from resolution_engine import generate_resolution
from database import (
    initialize_database,
    save_ticket,
    load_tickets,
    log_action,
    get_ticket_history,
)
from response_generator import generate_customer_response
from response_manager import (
    initialize_response_database,
    get_response,
    save_response,
    transition_response,
    get_response_history,
)


def verify_api_key(x_api_key: str | None = Header(default=None)):
    configured_key = os.getenv("OPSPILOT_API_KEY")

    if not configured_key:
        raise HTTPException(
            status_code=503,
            detail="API authentication is not configured.",
        )

    if not x_api_key or not secrets.compare_digest(
        x_api_key, configured_key
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key.",
        )


app = FastAPI(
    title="OpsPilot AI",
    version="0.3.0",
    dependencies=[Depends(verify_api_key)],
)



# ==================================================
# DATA MODELS
# ==================================================

class TicketIn(BaseModel):
    subject: str = Field(min_length=3, max_length=150)
    message: str = Field(min_length=10, max_length=2000)


class TicketOut(BaseModel):
    id: str
    subject: str
    message: str
    status: Literal[
        "new",
        "pending_approval",
        "in_progress",
        "approved",
        "rejected",
    ] = "new"
    assigned_department: str | None = None
    priority: str | None = None


class ApprovalDecision(BaseModel):
    approved: bool
    reviewer: str = Field(min_length=1)
    reason: str = Field(min_length=1)

class ResponseSaveIn(BaseModel):
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
    actor: str = Field(min_length=1)


class ResponseActionIn(BaseModel):
    actor: str = Field(min_length=1)
    reason: str = ""

# ==================================================
# DATABASE INITIALIZATION
# ==================================================

initialize_database()
initialize_response_database()

TICKETS: dict[str, TicketOut] = {
    ticket["id"]: TicketOut(**ticket)
    for ticket in load_tickets()
}
# ==================================================
# DEMO DATA INITIALIZATION
# ==================================================

def initialize_demo_tickets():
    if os.getenv("OPSPILOT_DEMO_MODE", "false").lower() != "true":
        return

    if TICKETS:
        return

    demo_tickets = [
        (
            "Incorrect subscription charge",
            "I was charged twice for my monthly subscription. "
            "Can someone review my billing and help me get a refund?"
        ),
        (
            "Unable to log into account",
            "I cannot access my account after resetting my password. "
            "Please help me restore access."
        ),
        (
            "Application crashes during checkout",
            "The application crashes every time I try to complete checkout. "
            "I have restarted the app but the issue continues."
        ),
        (
            "Request to update account information",
            "I need to update the email address associated with my account. "
            "What steps do I need to follow?"
        ),
        (
            "Question about refund policy",
            "I recently purchased a subscription and would like to know "
            "whether I qualify for a refund."
        ),
    ]

    for subject, message in demo_tickets:
        item = TicketOut(
            id=str(uuid4()),
            subject=subject,
            message=message,
        )

        save_ticket(item)
        TICKETS[item.id] = item

        log_action(
            ticket_id=item.id,
            action="ticket_created",
            details=f"Demo ticket created: {subject}",
        )


initialize_demo_tickets()

def find_ticket(ticket_id: str) -> TicketOut:
    ticket = TICKETS.get(ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


def build_ticket_analysis(ticket: TicketOut):
    analysis = analyze_ticket(
        subject=ticket.subject,
        message=ticket.message,
    )

    workflow = route_ticket(analysis)

    policies = retrieve_ticket_context(
        ticket.subject,
        ticket.message,
    )

    recommendation = generate_resolution(
        analysis=analysis,
        workflow=workflow,
        relevant_policies=policies,
    )

    return analysis, workflow, policies, recommendation


# ==================================================
# HEALTH
# ==================================================

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "OpsPilot AI",
    }


# ==================================================
# TICKET MANAGEMENT
# ==================================================

@app.post(
    "/tickets",
    response_model=TicketOut,
    status_code=201,
)
def create_ticket(ticket: TicketIn):
    item = TicketOut(
        id=str(uuid4()),
        **ticket.model_dump(),
    )

    save_ticket(item)
    TICKETS[item.id] = item

    log_action(
        ticket_id=item.id,
        action="ticket_created",
        details=f"Ticket created: {item.subject}",
    )

    return item


@app.get("/tickets", response_model=list[TicketOut])
def list_tickets():
    return list(TICKETS.values())


# ==================================================
# AI CLASSIFICATION
# ==================================================

@app.post("/tickets/{ticket_id}/analyze")
def analyze_existing_ticket(ticket_id: str):
    ticket = find_ticket(ticket_id)

    try:
        analysis = analyze_ticket(
            subject=ticket.subject,
            message=ticket.message,
        )

    except Exception as error:
        print(f"Ticket analysis failed: {error}")

        raise HTTPException(
            status_code=503,
            detail="Ticket analysis is temporarily unavailable.",
        ) from error

    return {
        "ticket_id": ticket_id,
        "analysis": analysis,
    }


# ==================================================
# KNOWLEDGE BASE
# ==================================================

@app.get("/knowledge/search")
def search_policies(query: str):
    results = search_knowledge_base(query)

    return {
        "query": query,
        "results": results,
        "total_results": len(results),
    }


@app.get("/tickets/{ticket_id}/knowledge")
def ticket_knowledge(ticket_id: str):
    ticket = find_ticket(ticket_id)

    policies = retrieve_ticket_context(
        ticket.subject,
        ticket.message,
    )

    return {
        "ticket_id": ticket_id,
        "relevant_policies": policies,
    }


# ==================================================
# RESOLUTION RECOMMENDATIONS
# ==================================================

@app.get("/tickets/{ticket_id}/recommendation")
def ticket_recommendation(ticket_id: str):
    ticket = find_ticket(ticket_id)

    try:
        (
            analysis,
            workflow,
            policies,
            recommendation,
        ) = build_ticket_analysis(ticket)

    except Exception as error:
        print(f"Recommendation generation failed: {error}")

        raise HTTPException(
            status_code=503,
            detail="Recommendation is temporarily unavailable.",
        ) from error

    return {
        "ticket_id": ticket_id,
        "analysis": analysis,
        "workflow": workflow,
        "relevant_policies": policies,
        "resolution_recommendation": recommendation,
    }


# ==================================================
# TICKET PROCESSING
# ==================================================

@app.post("/tickets/{ticket_id}/process")
def process_ticket(ticket_id: str):
    ticket = find_ticket(ticket_id)

    if ticket.status != "new":
        raise HTTPException(
            status_code=400,
            detail="Only new tickets can be processed.",
        )

    try:
        (
            analysis,
            workflow,
            relevant_policies,
            recommendation,
        ) = build_ticket_analysis(ticket)

    except Exception as error:
        print(f"Ticket processing failed: {error}")

        raise HTTPException(
            status_code=503,
            detail="Ticket processing is temporarily unavailable.",
        ) from error

    ticket.status = workflow["status"]
    ticket.assigned_department = workflow["assigned_department"]
    ticket.priority = workflow["priority"]

    save_ticket(ticket)

    log_action(
        ticket_id=ticket.id,
        action="ticket_processed",
        details=(
            f"Assigned to {ticket.assigned_department}, "
            f"priority: {ticket.priority}, "
            f"status: {ticket.status}, "
            f"policies retrieved: "
            f"{[p['id'] for p in relevant_policies]}"
        ),
    )

    return {
        "ticket_id": ticket_id,
        "analysis": analysis,
        "workflow": workflow,
        "relevant_policies": relevant_policies,
        "resolution_recommendation": recommendation,
        "updated_ticket": ticket,
    }


# ==================================================
# HUMAN APPROVAL
# ==================================================

@app.post("/tickets/{ticket_id}/approve")
def approve_ticket(
    ticket_id: str,
    decision: ApprovalDecision,
):
    ticket = find_ticket(ticket_id)

    if ticket.status != "pending_approval":
        raise HTTPException(
            status_code=400,
            detail="Ticket is not pending approval",
        )

    ticket.status = (
        "approved" if decision.approved else "rejected"
    )

    save_ticket(ticket)

    log_action(
        ticket_id=ticket.id,
        action=(
            "ticket_approved"
            if decision.approved
            else "ticket_rejected"
        ),
        details=(
            f"Reviewer: {decision.reviewer}. "
            f"Reason: {decision.reason}"
        ),
    )

    return {
        "ticket_id": ticket_id,
        "decision": ticket.status,
        "reviewer": decision.reviewer,
        "reason": decision.reason,
        "updated_ticket": ticket,
    }


# ==================================================
# AUDIT HISTORY
# ==================================================

@app.get("/tickets/{ticket_id}/history")
def ticket_history(ticket_id: str):
    find_ticket(ticket_id)

    return {
        "ticket_id": ticket_id,
        "history": get_ticket_history(ticket_id),
    }

# ==================================================
# CUSTOMER RESPONSE GENERATION
# ==================================================

@app.get("/tickets/{ticket_id}/response-draft")
def get_customer_response_draft(ticket_id: str):
    ticket = find_ticket(ticket_id)

    try:
        (
            analysis,
            workflow,
            policies,
            recommendation,
        ) = build_ticket_analysis(ticket)

        draft = generate_customer_response(
            ticket=ticket,
            analysis=analysis,
            recommendation=recommendation,
            policies=policies,
        )

    except Exception as error:
        print(f"Response generation failed: {error}")

        raise HTTPException(
            status_code=503,
            detail="Response drafting is temporarily unavailable.",
        ) from error

    return {
        "ticket_id": ticket_id,
        "draft": draft,
        "resolution_recommendation": recommendation,
        "relevant_policies": policies,
    }


# ==================================================
# RESPONSE MANAGEMENT API
# ==================================================

@app.get("/tickets/{ticket_id}/saved-response")
def read_saved_response(ticket_id: str):
    find_ticket(ticket_id)

    return {
        "ticket_id": ticket_id,
        "response": get_response(ticket_id),
    }


@app.post("/tickets/{ticket_id}/saved-response")
def write_saved_response(
    ticket_id: str,
    payload: ResponseSaveIn,
):
    find_ticket(ticket_id)

    try:
        response = save_response(
            ticket_id=ticket_id,
            subject=payload.subject,
            body=payload.body,
            actor=payload.actor,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {"response": response}


@app.post("/tickets/{ticket_id}/response-action/{action}")
def change_response_status(
    ticket_id: str,
    action: str,
    payload: ResponseActionIn,
):
    find_ticket(ticket_id)

    try:
        response = transition_response(
            ticket_id=ticket_id,
            action=action,
            actor=payload.actor,
            reason=payload.reason,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error

    return {"response": response}


@app.get("/tickets/{ticket_id}/response-history")
def read_response_history(ticket_id: str):
    find_ticket(ticket_id)

    return {
        "ticket_id": ticket_id,
        "history": get_response_history(ticket_id),
    }

# ==================================================
# AUTOMATED TICKET WORKFLOW
# ==================================================

@app.post("/tickets/{ticket_id}/automate")
def automate_ticket(ticket_id: str):
    ticket = find_ticket(ticket_id)

    if ticket.status != "new":
        raise HTTPException(
            status_code=400,
            detail="Only new tickets can be automated.",
        )

    if get_response(ticket_id) is not None:
        raise HTTPException(
            status_code=400,
            detail="This ticket already has a saved response.",
        )

    try:
        # Step 1: Classify ticket and retrieve policies
        analysis, workflow, policies, recommendation = (
            build_ticket_analysis(ticket)
        )

        # Step 2: Generate a customer response
        draft = generate_customer_response(
            ticket=ticket,
            analysis=analysis,
            recommendation=recommendation,
            policies=policies,
        )

        if not draft.get("subject") or not draft.get("body"):
            raise ValueError("Generated response is incomplete.")

    except Exception as error:
        print(f"Automation failed: {error}")

        raise HTTPException(
            status_code=503,
            detail="Automated workflow is temporarily unavailable.",
        ) from error

    # Step 3: Save the response draft
    try:
        saved_response = save_response(
            ticket_id=ticket_id,
            subject=draft["subject"],
            body=draft["body"],
            actor="OpsPilot Automation",
        )

    except Exception as error:
        print(f"Automation save failed: {error}")

        raise HTTPException(
            status_code=500,
            detail="Could not save automated response.",
        ) from error

    # Step 4: Update ticket routing
    ticket.status = workflow["status"]
    ticket.assigned_department = workflow["assigned_department"]
    ticket.priority = workflow["priority"]

    save_ticket(ticket)

    # Step 5: Record automation activity
    log_action(
        ticket_id=ticket.id,
        action="ticket_automated",
        details=(
            f"Department: {ticket.assigned_department}; "
            f"Priority: {ticket.priority}; "
            f"Status: {ticket.status}; "
            f"Response draft saved for human review."
        ),
    )

    return {
        "ticket_id": ticket_id,
        "automation_status": "completed",
        "analysis": analysis,
        "workflow": workflow,
        "relevant_policies": policies,
        "resolution_recommendation": recommendation,
        "response_draft": draft,
        "saved_response": saved_response,
        "updated_ticket": ticket,
        "automatically_sent": False,
    }
