# ADR 04: Replay Authorization Flow

## Status
Accepted

## Context
Users request historical graph states via the `ReplayEngine`. The challenge is that historical states might contain data that was governed differently in the past, or the user's current permissions should apply to historical reads.

## Decision
Replay authorization applies **Current Policies to Historical Data**.
- When `reconstruct_lineage` is called, it fetches the raw historical snapshot from the graph.
- Before returning, the entire snapshot is pushed through the *current* `GovernancePolicyEngine`.
- Restricted domains are masked from the historical output just as they would be in the live output.

## Consequences
- If a user loses access to a domain today, they cannot time-travel to read its past schema.
- Data governance cannot be bypassed via historical replays.
