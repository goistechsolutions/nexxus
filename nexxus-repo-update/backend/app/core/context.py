from dataclasses import dataclass
from uuid import UUID
@dataclass(frozen=True,slots=True)
class AnalysisContext:
 user_id:UUID; tenant_id:UUID; roles:frozenset[str]; correlation_id:str
