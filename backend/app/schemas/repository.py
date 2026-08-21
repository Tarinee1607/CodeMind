from datetime import datetime

from pydantic import BaseModel, ConfigDict


class RepositoryBase(BaseModel):
    name: str
    source_type: str
    source_url: str | None = None


class RepositoryCreate(RepositoryBase):
    pass

class RepositoryUpdate(BaseModel):
    name: str | None = None
    source_type: str | None = None
    source_url: str | None = None

class RepositoryResponse(RepositoryBase):
    id: int
    user_id: int
    local_path: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)