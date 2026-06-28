from pydantic import BaseModel
from typing import List, Optional
from hossagent.models.evidence import EvidenceItem

class Opportunity(BaseModel):
    account: str
    score: int
    confidence: str
    why: str
    recommended_action: str
    evidence: List[EvidenceItem] = []
    truth_status: Optional[str] = None
