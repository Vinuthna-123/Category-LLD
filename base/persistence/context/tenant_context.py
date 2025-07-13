class TenantContext:
    def __init__(self, tenant_id: str):
        self.tenant_id = tenant_id

    def get_tenant_id(self) -> str:
        return self.tenant_id
