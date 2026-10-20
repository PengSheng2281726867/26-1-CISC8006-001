# Real Git chronology

The course repository is independent. The author clone's history was neither
copied as nested `.git` nor reset. Target `https://github.com/PengSheng2281726867/26-1-CISC8006-001` was checked empty (size0,
branches[]) on2026-10-20; the authenticated account had push permission.

First real **local recovery-branch** import: `3d9b25b5918bd19eaba0ef8b2a61516113397a07` — `chore: import audited pre-git GAMMA research snapshot`.
It imports the already existing Baseline, MLP, LN/GELU and evidence **together**.
It is not the historical execution version of any registry run. No dates were
backdated and no synthetic Baseline-before-MLP history was constructed.

Following local commits record the actual addition of course documentation, sanity
checks and provenance adapters. Git author identity uses the authorized account's
public noreply address; AI_USAGE.md identifies the agent work and pending human review.

A `baseline-reconstructed-2026-10-20` tag may be created only after the copied Dot
network, its config and evaluation checks pass. It means reconstructed current
Baseline, not a historical checkpoint. It contains the current combined snapshot.
No Week12 final tag is created. Final course freeze date and approval are UNKNOWN.

Local HTTPS Git initially failed with the Windows schannel credential backend;
repository-local OpenSSL allows remote reads without a global setting change.
`gh` was unavailable; the connected GitHub app independently verified ownership,
permissions and remote emptiness. Normal Git push dry-run failed because this
process has no HTTPS username credential (interactive prompts disabled).
Publication is therefore being prepared through the already authorized GitHub
connector, without extracting a token or asking for a secret. The published
import is a new real commit at publication time containing Baseline and MLP
together; it does not pretend to replay development history.

Local recovery commits are retained on a separate `recovery-local` branch when
the published `main` is fetched. Branch creation/switching preserves both real
histories, with no reset, rebase, force push or fabricated parentage. Local
recovery commit hashes need not be publicly reachable; they are identified as
local, never as historical model-execution commits. The remote and local
published tree hashes must match. Publication status is verified only after
the connector updates main and Git fetch reads it back.
