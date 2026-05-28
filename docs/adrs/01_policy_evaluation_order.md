# ADR 01: Policy Evaluation Order

## Status
Accepted

## Context
Phase 14 introduces the `GovernancePolicyEngine` to enforce access controls, masking, and traversal boundaries. We must decide the strict evaluation order when multiple policies conflict (e.g. ALLOW vs DENY on the same namespace).

## Decision
The system will implement a **DENY-OVERRIDE** precedence model.
1. `DENY` policies take absolute precedence over all others. If any matched policy denies access, traversal is blocked.
2. `REDACT` drops entire nodes from visibility.
3. `MASK` obscures specific metadata attributes (e.g. replacing a field name with `***`).
4. `LIMIT_DEPTH` applies the most restrictive limit if multiple limits are found.
5. `ALLOW` is required for traversal. If no explicit allow exists, access is implicitly denied (default-deny).

## Consequences
- Guarantees fail-safe governance.
- Eliminates policy conflict ambiguity.
- Makes writing policies simpler (a single deny acts as a hard stop).
