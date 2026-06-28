from pydantic import BaseModel
from typing import Optional

class EvidenceItem(BaseModel):
    source: str
    title: str
    detail: str = ""
    url: Optional[str] = None
    date: Optional[str] = None
    raw_id: Optional[str] = None
