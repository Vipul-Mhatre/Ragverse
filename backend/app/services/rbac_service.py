from collections.abc import Iterable

ROLE_SOURCES: dict[str, set[str]] = {
    "admin": {"hr", "finance", "engineering", "security", "compliance"},
    "hr_manager": {"hr"},
    "hr_analyst": {"hr"},
    "finance_manager": {"finance", "hr"},
    "finance_analyst": {"finance"},
    "engineering_manager": {"engineering"},
    "engineering_analyst": {"engineering"},
    "security_manager": {"security"},
    "security_analyst": {"security"},
    "compliance_manager": {"compliance"},
    "compliance_analyst": {"compliance"},
}

ROLE_INHERITANCE: dict[str, set[str]] = {
    "admin": {
        "admin",
        "hr_manager",
        "hr_analyst",
        "finance_manager",
        "finance_analyst",
        "engineering_manager",
        "engineering_analyst",
        "security_manager",
        "security_analyst",
        "compliance_manager",
        "compliance_analyst",
    },
    "hr_manager": {"hr_manager", "hr_analyst"},
    "hr_analyst": {"hr_analyst"},
    "finance_manager": {"finance_manager", "finance_analyst"},
    "finance_analyst": {"finance_analyst"},
    "engineering_manager": {"engineering_manager", "engineering_analyst"},
    "engineering_analyst": {"engineering_analyst"},
    "security_manager": {"security_manager", "security_analyst"},
    "security_analyst": {"security_analyst"},
    "compliance_manager": {"compliance_manager", "compliance_analyst"},
    "compliance_analyst": {"compliance_analyst"},
}


def allowed_sources_for_role(role: str) -> set[str]:
    return ROLE_SOURCES.get(role, set())


def allowed_roles_for_role(role: str) -> set[str]:
    return ROLE_INHERITANCE.get(role, {role})


def filter_authorized_documents(role: str, docs: Iterable[dict]) -> list[dict]:
    allowed_sources = allowed_sources_for_role(role)
    allowed_roles = allowed_roles_for_role(role)
    return [
        d
        for d in docs
        if d.get("source") in allowed_sources and allowed_roles.intersection(d.get("allowed_roles", []))
    ]
