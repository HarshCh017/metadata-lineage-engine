from enum import Enum
from typing import List, Dict, Any, Optional
import structlog
from lineage_platform.errors.failure_taxonomy import PolicyViolationFailure, TraversalAuthorizationFailure
from lineage_platform.observability.telemetry import TelemetryManager

logger = structlog.get_logger()

class AccessControl(str, Enum):
    ALLOW = "ALLOW"
    DENY = "DENY"
    MASK = "MASK"
    REDACT = "REDACT"
    LIMIT_DEPTH = "LIMIT_DEPTH"
    LIMIT_REPLAY = "LIMIT_REPLAY"
    FILTER_RELATIONSHIP = "FILTER_RELATIONSHIP"

class GovernancePolicyEngine:
    """
    Centralized policy evaluation engine.
    Intercepts metadata payloads and applies DENY-OVERRIDE precedence masking.
    """
    
    def __init__(self, user_context: Dict[str, Any]):
        self.user_context = user_context
        # Mock policy store
        self.policies = {
            "finance.payments": AccessControl.MASK,
            "hr.employee": AccessControl.DENY,
            "shared.reference": AccessControl.ALLOW
        }

    def authorize_traversal(self, target_namespace: str) -> bool:
        """Determines if a traversal into a namespace is authorized."""
        policy = self.policies.get(target_namespace, AccessControl.DENY)
        
        if policy == AccessControl.DENY:
            TelemetryManager.POLICY_VIOLATIONS_TOTAL.inc()
            logger.warning("traversal_denied", namespace=target_namespace)
            raise TraversalAuthorizationFailure(f"Unauthorized to traverse namespace: {target_namespace}")
            
        TelemetryManager.NAMESPACE_TRAVERSAL_COUNT.inc()
        return True

    def apply_masking(self, payload: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Applies MASK and REDACT policies to a lineage payload BEFORE hash generation."""
        sanitized = []
        for node in payload:
            ns = node.get("namespace_id", "default")
            policy = self.policies.get(ns, AccessControl.DENY)
            
            if policy == AccessControl.DENY or policy == AccessControl.REDACT:
                TelemetryManager.POLICY_VIOLATIONS_TOTAL.inc()
                continue # Redact node completely
                
            if policy == AccessControl.MASK:
                # Obscure sensitive attributes
                node["name"] = "***MASKED***"
                node["expression"] = "***MASKED***"
                
            sanitized.append(node)
            
        return sanitized
