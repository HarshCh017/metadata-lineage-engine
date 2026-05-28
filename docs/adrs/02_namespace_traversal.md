# ADR 02: Namespace Traversal Semantics

## Status
Accepted

## Context
Lineage graphs cross organizational boundaries. We need rules for traversing from one domain namespace (e.g. `finance.payments`) to another (e.g. `shared.reference`).

## Decision
Namespace traversal is **Explicitly Authorized**.
- `QueryGovernanceEngine` will request cross-domain authorization from `GovernancePolicyEngine` on every edge hop that crosses a boundary.
- If a query originates in `Namespace A` and requests upstream lineage into `Namespace B`, the requestor must have read access to both namespaces.
- If access is denied, the traversal halts at the edge, returning a pseudo-node indicating a "Masked Cross-Domain Dependency".

## Consequences
- Prevents unauthorized graph exploration via backdoors.
- Allows domains to hide their internal implementations while exposing public interfaces.
