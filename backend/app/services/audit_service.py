import logging

logger = logging.getLogger("ragverse.audit")


def audit_log(event: str, user: str, details: str) -> None:
    logger.info("event=%s user=%s details=%s", event, user, details)
