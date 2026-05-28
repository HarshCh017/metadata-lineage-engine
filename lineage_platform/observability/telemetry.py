import structlog
from prometheus_client import Counter, Histogram, Gauge, REGISTRY

logger = structlog.get_logger()


class TelemetryManager:
    """
    Centralized Observability Layer.
    Consolidates parser metrics, Neo4j latency, and error rates.
    """
    FILES_PARSED: Counter
    PARSE_FAILURES: Counter
    FALLBACK_RATES: Counter
    INCLUDES_RESOLVED: Counter
    MACRO_EXPANSIONS: Counter

    PARSER_CONFIDENCE: Histogram
    PARTIAL_RECOVERIES: Counter
    UNRESOLVED_INCLUDES: Counter
    TRANSFORMATION_DENSITY: Histogram
    NORMALIZATION_MUTATIONS: Counter

    GRAPH_INSERT_LATENCY: Histogram
    PARSE_LATENCY: Histogram

    LINEAGE_CONFIDENCE_SCORE: Histogram
    TEMPORAL_QUERY_LATENCY: Histogram
    GRAPH_INTEGRITY_FAILURES: Counter
    ORPHAN_NODE_COUNT: Histogram
    RECOVERY_ENGINE_ACTIVATIONS: Counter
    SEMANTIC_VALIDATION_FAILURES: Counter
    LINEAGE_DRIFT_RATE: Histogram

    POLICY_VIOLATIONS_TOTAL: Counter
    TRUST_DEGRADATION_RATE: Histogram
    REPLAY_AUTHORIZATION_FAILURES: Counter
    NAMESPACE_TRAVERSAL_COUNT: Counter
    WORKLOAD_QUEUE_DEPTH: Gauge
    DISTRIBUTED_SCAN_LATENCY: Histogram
    FEDERATED_REPLAY_DURATION: Histogram

    _initialized = False

    @classmethod
    def init_metrics(cls):
        if cls._initialized:
            return

        def get_or_create_counter(name, desc):
            if name + "_total" in REGISTRY._names_to_collectors:
                return REGISTRY._names_to_collectors[name + "_total"]
            return Counter(name + "_total", desc)

        def get_or_create_histogram(name, desc):
            if name in REGISTRY._names_to_collectors:
                return REGISTRY._names_to_collectors[name]
            return Histogram(name, desc)

        def get_or_create_gauge(name, desc):
            if name in REGISTRY._names_to_collectors:
                return REGISTRY._names_to_collectors[name]
            return Gauge(name, desc)

        cls.FILES_PARSED = get_or_create_counter("qlikview_files_parsed", "Total QlikView files parsed")
        cls.PARSE_FAILURES = get_or_create_counter("qlikview_parse_failures", "Total parse failures")
        cls.FALLBACK_RATES = get_or_create_counter("qlikview_fallback_parse", "Total regex fallbacks triggered")
        cls.INCLUDES_RESOLVED = get_or_create_counter("qlikview_includes_resolved", "Total $(Include=...) directives resolved")
        cls.MACRO_EXPANSIONS = get_or_create_counter("qlikview_macro_expansions", "Total $(var) macro expansions performed")

        # Phase 11 Maturity Metrics
        cls.PARSER_CONFIDENCE = get_or_create_histogram("qlikview_parser_confidence", "Score (0-100) indicating AST completeness and deterministic lineage")
        cls.PARTIAL_RECOVERIES = get_or_create_counter("qlikview_partial_recovery", "Count of AST failures partially recovered by regex")
        cls.UNRESOLVED_INCLUDES = get_or_create_counter("qlikview_unresolved_include", "Count of unresolvable include directives")
        cls.TRANSFORMATION_DENSITY = get_or_create_histogram("qlikview_transformation_density", "Ratio of physical fields to transform operations")
        cls.NORMALIZATION_MUTATIONS = get_or_create_counter("qlikview_normalization_mutations", "Count of field deduplications and FQN normalizations")

        cls.GRAPH_INSERT_LATENCY = get_or_create_histogram("neo4j_batch_insert_seconds", "Latency of Neo4j graph batch writes")
        cls.PARSE_LATENCY = get_or_create_histogram("qlikview_parse_latency_seconds", "Latency of QlikView parsing phase")

        # Phase 13 Governance Metrics
        cls.LINEAGE_CONFIDENCE_SCORE = get_or_create_histogram("lineage_confidence_score", "Multi-dimensional confidence score of semantic lineage")
        cls.TEMPORAL_QUERY_LATENCY = get_or_create_histogram("temporal_query_latency_seconds", "Latency of historical temporal queries")
        cls.GRAPH_INTEGRITY_FAILURES = get_or_create_counter("graph_integrity_failures", "Count of graph structural or temporal integrity violations")
        cls.ORPHAN_NODE_COUNT = get_or_create_histogram("orphan_node_count", "Number of disconnected or orphaned nodes discovered during compaction")
        cls.RECOVERY_ENGINE_ACTIVATIONS = get_or_create_counter("recovery_engine_activations", "Count of parser recovery engine salvages")
        cls.SEMANTIC_VALIDATION_FAILURES = get_or_create_counter("semantic_validation_failures", "Count of failed semantic validation assertions")
        cls.LINEAGE_DRIFT_RATE = get_or_create_histogram("lineage_drift_rate", "Velocity of lineage structural changes over time")

        # Phase 14 Federated Metrics
        cls.POLICY_VIOLATIONS_TOTAL = get_or_create_counter("policy_violations_total", "Total policy violations encountered")
        cls.TRUST_DEGRADATION_RATE = get_or_create_histogram("trust_degradation_rate", "Rate of trust degradation across lineage chains")
        cls.REPLAY_AUTHORIZATION_FAILURES = get_or_create_counter("replay_authorization_failures", "Count of failed replay authorizations")
        cls.NAMESPACE_TRAVERSAL_COUNT = get_or_create_counter("namespace_traversal_count", "Count of cross-namespace traversals")
        cls.WORKLOAD_QUEUE_DEPTH = get_or_create_gauge("workload_queue_depth", "Current depth of workload queues")
        cls.DISTRIBUTED_SCAN_LATENCY = get_or_create_histogram("distributed_scan_latency_seconds", "Latency of distributed integrity scans")
        cls.FEDERATED_REPLAY_DURATION = get_or_create_histogram("federated_replay_duration_seconds", "Duration of federated replays")

        cls._initialized = True


# Initialize metrics on import
TelemetryManager.init_metrics()
