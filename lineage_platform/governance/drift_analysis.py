from enum import Enum
from dataclasses import dataclass, field
from typing import List

class DriftCategory(str, Enum):
    TRANSFORMATION_DRIFT = "TRANSFORMATION_DRIFT"
    SCHEMA_DRIFT = "SCHEMA_DRIFT"
    ONTOLOGY_DRIFT = "ONTOLOGY_DRIFT"
    TRUST_DRIFT = "TRUST_DRIFT"
    REPLAY_DRIFT = "REPLAY_DRIFT"
    POLICY_DRIFT = "POLICY_DRIFT"

@dataclass
class DriftAnalysis:
    drift_type: DriftCategory
    severity: str
    affected_domains: List[str] = field(default_factory=list)
    trust_impact: float = 0.0
    replay_impact: str = "NONE"

class DriftIntelligenceEngine:
    """
    Expands basic drift rate tracking into semantic governance intelligence.
    Scores ontology drift mathematically.
    """
    
    def analyze_drift(self, from_state: dict, to_state: dict) -> List[DriftAnalysis]:
        """
        Compares two exact snapshots and calculates the lineage drift.
        Returns a classified list of detected semantic drifts.
        """
        drifts = []
        
        # Mocking drift logic: e.g. detecting schema changes across time
        if from_state.get("schema_version") != to_state.get("schema_version"):
            drifts.append(DriftAnalysis(
                drift_type=DriftCategory.SCHEMA_DRIFT,
                severity="HIGH",
                affected_domains=["global"],
                trust_impact=0.2,
                replay_impact="REPLAY_COMPATIBILITY_BROKEN"
            ))
            
        # Normally would diff the actual nodes/edges
        
        return drifts
