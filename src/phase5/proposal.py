from dataclasses import dataclass
from typing import Literal
from datetime import datetime
import uuid

ProposalStatus = Literal["pending", "accepted", "edited", "rejected"]

@dataclass
class Proposal:
    proposal_id: str
    source: Literal["llm"]
    context: str
    generated_at: str
    status: ProposalStatus
    text: str

    @staticmethod
    def create(text: str, context: str) -> "Proposal":
        return Proposal(
            proposal_id=str(uuid.uuid4()),
            source="llm",
            context=context,
            generated_at=datetime.utcnow().isoformat(),
            status="pending",
            text=text,
        )

