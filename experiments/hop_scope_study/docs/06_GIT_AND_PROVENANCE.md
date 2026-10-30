# Git, provenance and publication evidence

Base target main: `935a4303ed0d1410e29d9374cc1ce91b82dc527c`.
Upstream author code: `36d054b4ae53c0c8e360d85d056f5207d61c8281`, MIT;
see repository NOTICE and research/upstream_snapshot/LICENSE. The new adapter
inherits immutable research components; scientific source hashes are captured
per execution. Data/reference tensor parity is recorded separately.

Target repository:
[26-1-CISC8006-001](https://github.com/PengSheng2281726867/26-1-CISC8006-001).
Remote independent branch:
[exp/fixed-k-hop-gating](https://github.com/PengSheng2281726867/26-1-CISC8006-001/tree/exp/fixed-k-hop-gating).
The branch was created through the authorized GitHub connection from the base
main SHA after checking no such branch existed. Main was not changed.

## Execution version versus publication version

Local clone metadata was owned by a sandbox process; subsequent FETCH_HEAD/ref
lock writes were denied. Another process identity also required per-command
safe.directory for read-only queries. No global Git setting, original workspace,
protected metadata permission or old history was changed. A request for sandbox
escalation was rejected by policy, and no escalation was used.

Scientific runs therefore accurately record the base main commit plus dirty=true
and full scientific source/config/data/split/initialization hashes. They were
not executed at a later publication SHA. The local worktree branch remains main
because ref writes were unavailable; this does not authorize pushing it to main.
No trained historical checkpoint was reused. Twelve new verified Pilot cells are
reused only within this new300-cell matrix.

## Exact publication process

The publication_snapshot.py adapter creates a new candidate Git index and object
store **inside the external writable run directory**, reading the clone's objects
as an alternate. It writes no refs or original .git files. Explicit paths only:
new experiments/hop_scope_study plus minimal appended README, AI_USAGE and
IMPROVEMENTS navigation/evidence. core.autocrlf=false preserves the actual source
bytes hashed during execution; every index blob is checked against its local file.

The existing scripts/check_publication.py reads this **entire exact index** with
inherited Git environment, including historical files. Staged diff/stat and the
check receipt stay local. A local commit object may be created after the check.
Publication uses a normal non-force push if credentials permit, or the authorized
GitHub connection: upload exact reviewed blobs, build a tree matching the audited
local tree SHA, create a child commit of the recorded main SHA and fast-forward
only the independent branch. Main remains untouched. Source hashes and tree
identity, not a claim about a dirty checkout being clean, establish correspondence.

Final remote commit SHA, observed branch head, push/connector outcome and PR URL
are recorded in the local publication receipt and final delivery message.
See the branch's actual Git history for the authoritative publication commit.
If network/permission verification fails, retain a local commit and report the
publication as blocked, not uploaded. No force push, rebase, merge or final tag.

Original and target protected-file before/after evidence is summarized in
results/preservation.json when the final preservation audit completes. No full
private source paths, raw dataset/split arrays, predictions, weights, secrets or
local conversation export are included in public artifacts.
