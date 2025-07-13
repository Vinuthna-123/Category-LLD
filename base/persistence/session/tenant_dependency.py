from core.database import SessionLocal
from base.persistence.session.tenant_session import TenantSession

def get_tenant_session():
    db = SessionLocal()
    try:
        yield TenantSession(db=db, tenant_context=None)
    finally:
        db.close()
