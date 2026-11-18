
from database import initialize_database, log_action

initialize_database()

log_action(
    ticket_id="test-123",
    action="ticket_created",
    details="Test audit log entry"
)

print("Audit log saved successfully!")
