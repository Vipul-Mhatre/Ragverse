def route_sources(intent: str) -> list[str]:
    if intent == "compliance":
        return ["compliance"]
    if intent == "security":
        return ["security"]
    if intent == "finance":
        return ["finance"]
    if intent == "hr":
        return ["hr"]
    if intent == "engineering":
        return ["engineering"]
    if intent == "cross_source":
        return ["finance", "security", "hr"]
    return ["hr", "finance", "engineering", "security", "compliance"]
