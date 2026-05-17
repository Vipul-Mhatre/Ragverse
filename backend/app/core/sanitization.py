import re

INJECTION_PATTERNS = [
    r"ignore\s+all\s+previous\s+instructions",
    r"reveal\s+system\s+prompt",
    r"bypass\s+security",
    r"show\s+hidden\s+data",
    r"disclose\s+admin",
    r"developer\s+instructions",
    r"system\s+prompt",
    r"exfiltrate",
]


def sanitize_query(query: str) -> str:
    clean = " ".join(query.strip().split())
    return re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F]", "", clean)


def has_prompt_injection(query: str) -> bool:
    lowered = query.lower()
    return any(re.search(p, lowered) for p in INJECTION_PATTERNS)
