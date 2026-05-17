def classify_intent(query: str) -> str:
    lowered = query.lower()
    if any(k in lowered for k in ["correlate", "associated", "across", "between"]):
        return "cross_source"
    if any(k in lowered for k in ["gdpr", "sox", "audit", "compliance"]):
        return "compliance"
    if any(k in lowered for k in ["login", "auth", "mfa", "incident", "security"]):
        return "security"
    if any(k in lowered for k in ["budget", "revenue", "finance", "cost"]):
        return "finance"
    if any(k in lowered for k in ["payroll", "salary", "hr", "benefits"]):
        return "hr"
    if any(k in lowered for k in ["architecture", "api", "engineering", "service"]):
        return "engineering"
    return "general"
