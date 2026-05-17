from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    role: str


USERS: dict[str, User] = {
    "alice": User(username="alice", role="hr_manager"),
    "bob": User(username="bob", role="engineering_manager"),
    "carol": User(username="carol", role="finance_manager"),
    "diana": User(username="diana", role="admin"),
}


def authenticate(username: str) -> User | None:
    return USERS.get(username)
