def route_sources(intent: str) -> list[str]:
    if intent == "compliance":
        return ["compliance", "pdf", "json"]
    if intent == "operations":
        return ["operations", "sql", "csv", "json"]
    return ["pdf", "csv", "json", "sql", "compliance", "operations"]
