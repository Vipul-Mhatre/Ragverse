def classify_intent(query: str) -> str:
    lowered = query.lower()
    if any(k in lowered for k in ["policy", "compliance", "audit"]):
        return "compliance"
    if any(k in lowered for k in ["incident", "ops", "uptime", "latency"]):
        return "operations"
    return "general"
