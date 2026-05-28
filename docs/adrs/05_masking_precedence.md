# ADR 05: Masking Precedence Rules

## Status
Accepted

## Context
When sensitive nodes are encountered during graph traversal or export, they must be redacted. We must ensure deterministic hashes are not poisoned by masked data, avoiding metadata leakage via hash brute-forcing.

## Decision
Masking occurs **BEFORE** replay manifest hash generation and JSON serialization.
- `GovernancePolicyEngine` iterates over the output graph in memory.
- `MASK` policies overwrite the attribute in-memory with `"***MASKED***"`.
- `REDACT` policies completely pop the node from the returned collection, severing the visible edge.
- Only after this sanitized view is built is the SHA-256 manifest hash generated.

## Consequences
- Masked data is cryptographically unrecoverable from the output or the manifest hash.
- Upstream developers debugging hashes must understand their authorization level impacts the generated hash.
