import hashlib


def generate_deterministic_id(canonical_str: str) -> str:
    """
    Generate a deterministic, cross-parser-safe node ID.

    Uses SHA-256 truncated to 16 hex chars.
    Canonical string format: "<label>::<unique_attributes>"

    Examples:
        generate_deterministic_id("table::PROD.SALES.ORDERS")
        generate_deterministic_id("attribute::app.table.field")
    """
    return hashlib.sha256(canonical_str.encode()).hexdigest()[:16]
