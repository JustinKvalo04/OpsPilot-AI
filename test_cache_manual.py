
from database import (
    initialize_database,
    generate_cache_key,
    get_cached_analysis,
    save_cached_analysis
)

initialize_database()

subject = "Duplicate charge"
message = "I was charged twice for my subscription."
mode = "mock"

# Generate a unique key for this request
key = generate_cache_key(subject, message, mode)

# Check whether we already have a saved result
cached = get_cached_analysis(key)

if cached is None:
    print("CACHE MISS - Saving a new analysis")

    analysis = {
        "category": "billing",
        "priority": "high",
        "department": "finance",
        "requires_human_review": True,
        "mode": "mock"
    }

    save_cached_analysis(key, analysis)

else:
    print("CACHE HIT - Reusing saved analysis")
    analysis = cached

print(analysis)
