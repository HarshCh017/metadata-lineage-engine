import structlog
from prometheus_client import Counter, Histogram, REGISTRY

logger = structlog.get_logger()

class TelemetryManager:
    """
    Centralized Observability Layer.
    Consolidates parser metrics, Neo4j latency, and error rates.
    """
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
        
        cls._initialized = True

# Initialize metrics on import
TelemetryManager.init_metrics()
