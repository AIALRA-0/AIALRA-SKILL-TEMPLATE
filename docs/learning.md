# Controlled learning

## Three layers

1. Stable core: workflow, schemas, scripts, validators, instructions, permissions, and core lock. Runtime learning cannot write here.
2. Active advisory rules: a bounded set injected into Runner directives. Core and current user instructions always win.
3. Raw event history: one sanitized event per run, stored in the active ledger until losslessly archived.

## Event contract

An event records polarity, kebab-case scope, one sanitized sentence, a controlled evidence identifier, source hash, required state ID, timestamp, and promotion flag. The complete ledger and archives enforce at most one event for each state ID.

Accepted evidence prefixes are:

- `validator:`
- `executor:`
- `review:`
- `user-confirmed:`

The learning command does not accept raw prompts, raw page content, or full tool output. It removes credential patterns, emails, URLs, and long numeric identifiers, and restricts the final sentence to 12–240 characters.

## Lossless compaction

Strict semantic compression cannot guarantee both arbitrary text halving and no information loss. The runtime therefore separates storage size from active context size.

At the default threshold of 32 events:

1. The exact events are written to a content-addressed JSONL archive.
2. The active ledger is truncated only after the archive is safely written.
3. Exact normalized duplicates are merged deterministically with polarity counts and source event IDs.
4. Active rules are ranked by support and bounded to 16.
5. Events not selected for active context remain fully available in archives and Git history.

Compaction is protected by an exclusive lock. Archive hash collisions or archive modification are hard failures.

## Promotion

`promote.py` produces a proposal only. It never edits `workflow.yaml`, schemas, scripts, validators, `SKILL.md`, or `.core-lock.json`.

Normal eligibility requires at least three supporting events. A single serious safety event may create a proposal only when explicitly user-confirmed. Every proposal starts with all gates incomplete:

- contradiction review;
- regression test;
- workflow and core tests;
- version bump;
- human approval;
- regenerated core lock.

The core is changed in a separate reviewed task after these gates are satisfied.
