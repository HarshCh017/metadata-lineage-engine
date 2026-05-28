from dataclasses import dataclass, field
from typing import List, Dict, Any
import structlog
from lineage_platform.observability.telemetry import TelemetryManager

logger = structlog.get_logger()


@dataclass
class TrustEvaluation:
    overall_confidence: float
    weakest_link: str
    degraded_segments: List[str] = field(default_factory=list)
    inferred_segments: List[str] = field(default_factory=list)
    unresolved_segments: List[str] = field(default_factory=list)


class TrustPropagationEngine:
    """
    Transforms local parser confidence into graph-wide trust propagation.
    Applies Multiplicative and Minimum-Bounded degradation to lineage paths.
    """

    def evaluate_lineage_trust(self, path_nodes: List[Dict[str, Any]]) -> TrustEvaluation:
        """
        Evaluates a sequentially ordered path of lineage nodes.
        Assumes path_nodes is ordered from Source -> Target.
        """
        if not path_nodes:
            return TrustEvaluation(overall_confidence=1.0, weakest_link="none")

        current_trust = 1.0
        weakest = "none"
        min_seen = 1.0

        eval_result = TrustEvaluation(overall_confidence=1.0, weakest_link="none")

        for node in path_nodes:
            # Assuming nodes carry a baseline 'local_confidence' from parsing phase
            local_conf = node.get("confidence_aggregate", 1.0)

            # Trust equation: N.local * MIN(Upstream)
            current_trust = local_conf * min_seen

            if current_trust < min_seen:
                min_seen = current_trust
                weakest = node.get("name", "unknown_node")

            if local_conf < 0.8:
                eval_result.degraded_segments.append(node.get("name", "unknown_node"))

            if node.get("inferred", False):
                eval_result.inferred_segments.append(node.get("name", "unknown_node"))

            if node.get("unresolved", False):
                eval_result.unresolved_segments.append(node.get("name", "unknown_node"))

        eval_result.overall_confidence = current_trust
        eval_result.weakest_link = weakest

        # Telemetry
        if current_trust < 1.0:
            # Rate of degradation = 1.0 - final trust
            TelemetryManager.TRUST_DEGRADATION_RATE.observe(1.0 - current_trust)

        return eval_result
