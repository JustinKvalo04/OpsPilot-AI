
from database import (
    initialize_database,
    get_live_ai_call_count,
    reserve_live_ai_call
)

initialize_database()

# Use a temporary limit equal to the current count.
# This tests rejection without consuming any reservations.
current_count = get_live_ai_call_count()

allowed = reserve_live_ai_call(current_count)

print("Request allowed:", allowed)
print("Live AI calls:", get_live_ai_call_count())

assert allowed is False
print("PASS - Request limit correctly blocked")
