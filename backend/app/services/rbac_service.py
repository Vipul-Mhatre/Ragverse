from collections.abc import Iterable

ROLE_PERMISSIONS: dict[str, set[str]] = {
    "admin": {"pdf", "csv", "sql", "json", "compliance", "operations"},
    "analyst": {"pdf", "csv", "json", "operations"},
    "guest": {"pdf"},
}


def allowed_sources_for_role(role: str) -> set[str]:
    return ROLE_PERMISSIONS.get(role, set())


def filter_authorized_documents(role: str, docs: Iterable[dict]) -> list[dict]:
    allowed_sources = allowed_sources_for_role(role)
    return [
        d
        for d in docs
        if d.get("source") in allowed_sources and role in set(d.get("allowed_roles", []))
    ]
