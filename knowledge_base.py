
import json
import re
from pathlib import Path

POLICY_FILE = Path(__file__).resolve().parent / "company_policies.json"

STOP_WORDS = {
    "the", "and", "for", "with", "this", "that",
    "from", "have", "been", "was", "are", "you",
    "your", "can", "will", "would", "about",
    "into", "when", "what", "need", "want",
    "please", "customer", "customers"
}


def load_policies():
    with open(POLICY_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def tokenize(text):
    words = re.findall(r"[a-z0-9]+", text.lower())

    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def search_knowledge_base(query: str, limit: int = 3):
    """
    Search company policies using keyword relevance.
    Returns the most relevant matching documents.
    """

    if not 1 <= limit <= 10:
        raise ValueError("Limit must be between 1 and 10")

    policies = load_policies()
    query_words = tokenize(query)

    results = []

    for policy in policies:
        keywords = tokenize(" ".join(policy["keywords"]))
        title_words = tokenize(policy["title"])
        content_words = tokenize(policy["content"])

        keyword_matches = query_words.intersection(keywords)
        title_matches = query_words.intersection(title_words)
        content_matches = query_words.intersection(content_words)

        score = (
            len(keyword_matches) * 5
            + len(title_matches) * 3
            + len(content_matches)
        )

        if score > 0:
            results.append({
                "id": policy["id"],
                "title": policy["title"],
                "category": policy["category"],
                "content": policy["content"],
                "relevance_score": score
            })

    results.sort(
        key=lambda item: item["relevance_score"],
        reverse=True
    )

    return results[:limit]


def retrieve_ticket_context(subject: str, message: str):
    query = f"{subject} {message}"

    return search_knowledge_base(query, limit=3)
