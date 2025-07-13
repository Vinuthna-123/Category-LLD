from sqlalchemy.orm import Session

class TenantSession:
    def __init__(self, db: Session, tenant_context):
        self.db = db
        self.tenant_context = tenant_context

    def query(self, *args, **kwargs):
        return self.db.query(*args, **kwargs)

    def add(self, instance):
        return self.db.add(instance)

    def delete(self, instance):
        return self.db.delete(instance)

    def commit(self):
        return self.db.commit()
    
    def refresh(self, instance):
        return self.db.refresh(instance)

    def get(self, model, id):
        return self.db.get(model, id)

    def rollback(self):
        return self.db.rollback()
