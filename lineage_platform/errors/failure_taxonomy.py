from enum import Enum
from typing import Optional


class Severity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Recoverability(str, Enum):
    FULLY_RECOVERABLE = "FULLY_RECOVERABLE"
    PARTIALLY_RECOVERABLE = "PARTIALLY_RECOVERABLE"
    UNRECOVERABLE = "UNRECOVERABLE"


class GovernanceException(Exception):
    """Base class for all governance-grade lineage exceptions."""

    def __init__(
        self,
        message: str,
        severity: Severity,
        recoverability: Recoverability,
        confidence_impact: float,
        affected_lineage_scope: Optional[str] = None
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.recoverability = recoverability
        self.confidence_impact = confidence_impact
        self.affected_lineage_scope = affected_lineage_scope


class ParserFailure(GovernanceException):
    def __init__(self, message: str, confidence_impact: float = 0.5):
        super().__init__(
            message,
            severity=Severity.ERROR,
            recoverability=Recoverability.PARTIALLY_RECOVERABLE,
            confidence_impact=confidence_impact,
            affected_lineage_scope="script_ast"
        )


class TemporalIntegrityFailure(GovernanceException):
    def __init__(self, message: str):
        super().__init__(
            message,
            severity=Severity.CRITICAL,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope="graph_temporal_window"
        )


class SemanticValidationFailure(GovernanceException):
    def __init__(self, message: str, confidence_impact: float = 1.0):
        super().__init__(
            message,
            severity=Severity.ERROR,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=confidence_impact,
            affected_lineage_scope="semantic_ontology"
        )


class SnapshotReplayFailure(GovernanceException):
    def __init__(self, message: str):
        super().__init__(
            message,
            severity=Severity.ERROR,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope="temporal_snapshot"
        )


class GraphIntegrityFailure(GovernanceException):
    def __init__(self, message: str, severity: Severity = Severity.CRITICAL):
        super().__init__(
            message,
            severity=severity,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope="graph_ontology"
        )


class RecoveryFailure(GovernanceException):
    def __init__(self, message: str):
        super().__init__(
            message,
            severity=Severity.CRITICAL,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope="parser_fallback"
        )


class GovernancePolicyViolation(GovernanceException):
    def __init__(self, message: str):
        super().__init__(
            message,
            severity=Severity.CRITICAL,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=0.0,
            affected_lineage_scope="query_access"
        )


class TraversalBudgetExceeded(GovernanceException):
    """Raised by QueryGovernanceEngine when a query attempts to scan too many nodes."""

    def __init__(self, message: str):
        super().__init__(
            message,
            severity=Severity.ERROR,
            recoverability=Recoverability.FULLY_RECOVERABLE,
            confidence_impact=0.0,
            affected_lineage_scope="query_engine"
        )

# Phase 14 Federated Failures


class PolicyViolationFailure(GovernanceException):
    def __init__(self, message: str, namespace: str):
        super().__init__(
            message,
            severity=Severity.CRITICAL,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope=namespace
        )


class NamespaceIsolationFailure(GovernanceException):
    def __init__(self, message: str, namespace: str):
        super().__init__(
            message,
            severity=Severity.CRITICAL,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope=namespace
        )


class TrustPropagationFailure(GovernanceException):
    def __init__(self, message: str, namespace: str):
        super().__init__(
            message,
            severity=Severity.ERROR,
            recoverability=Recoverability.PARTIALLY_RECOVERABLE,
            confidence_impact=0.5,
            affected_lineage_scope=namespace
        )


class ReplayGovernanceFailure(GovernanceException):
    def __init__(self, message: str, namespace: str):
        super().__init__(
            message,
            severity=Severity.CRITICAL,
            recoverability=Recoverability.UNRECOVERABLE,
            confidence_impact=1.0,
            affected_lineage_scope=namespace
        )


class TraversalAuthorizationFailure(GovernanceException):
    def __init__(self, message: str):
        super().__init__(
            message,
            severity=Severity.ERROR,
            recoverability=Recoverability.FULLY_RECOVERABLE,
            confidence_impact=0.0,
            affected_lineage_scope="cross_domain_edge"
        )


class WorkloadStarvationFailure(GovernanceException):
    def __init__(self, message: str, namespace: str):
        super().__init__(
            message,
            severity=Severity.WARNING,
            recoverability=Recoverability.FULLY_RECOVERABLE,
            confidence_impact=0.0,
            affected_lineage_scope=namespace
        )
