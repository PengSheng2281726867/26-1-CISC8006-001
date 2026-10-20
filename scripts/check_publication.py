"""Audit the exact Git index before a public commit; never print matched secrets."""
from pathlib import Path
import hashlib
import json
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.pt', '.pth', '.ckpt', '.npz', '.npy', '.pkl', '.pickle', '.zip', '.pdf', '.parquet'}
PATTERNS = {
    'github_token': r'\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    'openai_key': r'\bsk-(?:proj-)?[A-Za-z0-9_-]{30,}',
    'aws_access_key': r'\b(?:AKIA|ASIA)[A-Z0-9]{16}\b',
    'private_key': r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
    'windows_private_path': r'[A-Za-z]:[\\/]+(?:Users|Code|Environment)[\\/]',
    'unix_private_path': r'/(?:home|Users)/[A-Za-z0-9_.-]+/',
}


def inspect():
    result = subprocess.run(['git', 'ls-files', '--stage', '-z'], cwd=ROOT,
                            capture_output=True, check=True)
    findings, entries = [], []
    for entry in result.stdout.split(b'\0'):
        if not entry: continue
        info, path_bytes = entry.split(b'\t', 1)
        mode, oid, stage = info.decode().split()
        rel = path_bytes.decode('utf-8')
        path = Path(rel)
        if mode != '100644' or stage != '0':
            findings.append(dict(path=rel, kind='non_regular_or_conflicted_index_entry'))
        if (path.name == '.env' or path.name.startswith('.env.') or
            path.suffix.lower() in FORBIDDEN or '.git' in path.parts or
            any(part.lower() in ('.aws', '.codex', '.agents', 'data', 'checkpoints', 'outputs') for part in path.parts)):
            findings.append(dict(path=rel, kind='forbidden_artifact_name'))
        data = subprocess.check_output(['git', 'show', ':' + rel], cwd=ROOT)
        if len(data) > 10 * 1024 * 1024:
            findings.append(dict(path=rel, kind='over_10MiB'))
        if path.suffix.lower() not in ('.png', '.svg'):
            try: content = data.decode('utf-8-sig')
            except UnicodeDecodeError:
                findings.append(dict(path=rel, kind='unreviewed_binary'))
                content = ''
            for label, regex in PATTERNS.items():
                if re.search(regex, content): findings.append(dict(path=rel, kind=label))
        entries.append(dict(path=rel, bytes=len(data), sha256=hashlib.sha256(data).hexdigest()))
    return dict(status='passed' if not findings else 'failed', files=len(entries),
                bytes=sum(e['bytes'] for e in entries), findings=findings,
                check='Git index content, not just working tree', credentials_printed=False)


if __name__ == '__main__':
    report = inspect()
    print(json.dumps(report, indent=2))
    sys.exit(0 if report['status'] == 'passed' else 1)
