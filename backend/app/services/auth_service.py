from dataclasses import dataclass


@dataclass(frozen=True)
class User:
    username: str
    role: str


USERS: dict[str, User] = {
    "alice": User(username="alice", role="admin"),
    "bob": User(username="bob", role="analyst"),
    "eve": User(username="eve", role="guest"),
}


def authenticate(username: str) -> User | None:
    return USERS.get(username)
