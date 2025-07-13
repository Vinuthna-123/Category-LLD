import uuid

def generate_primary_key(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"
