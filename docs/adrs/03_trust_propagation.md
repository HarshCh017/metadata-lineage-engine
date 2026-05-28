# ADR 03: Trust Propagation Rules

## Status
Accepted

## Context
Metadata confidence is calculated locally at parse time. However, a downstream dataset's trustworthiness relies heavily on its upstream sources.

## Decision
Trust degradation is **Multiplicative and Minimum-Bounded**.
- A transformation node inherits the minimum confidence score of all its direct upstream dependencies, multiplied by its own parser-assigned confidence.
- Equation: `Trust(N) = N.local_confidence * MIN(Trust(Parent_1), ..., Trust(Parent_N))`
- A graph traversal will return an overall `TrustEvaluation` summarizing the entire chain.

## Consequences
- Weak upstream links naturally poison downstream trust.
- Inferred segments propagate uncertainty correctly.
