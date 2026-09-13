"""Ensure staged skill/evidence blob bytes equal the locally verified files."""
import hashlib
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
rows = subprocess.check_output(['git', 'ls-files', '-s', '-z'], cwd=ROOT).split(b'\0')
entries = []
for row in rows:
    if not row:
        continue
    meta, name = row.split(b'\t', 1)
    path = name.decode()
    if path.startswith(('skills/', 'docs/research/full-release/')):
        entries.append((meta.split()[1], path))
proc = subprocess.Popen(['git', 'cat-file', '--batch'], cwd=ROOT,
                        stdin=subprocess.PIPE, stdout=subprocess.PIPE)
content, _ = proc.communicate(b'\n'.join(oid for oid, _ in entries)+b'\n')
assert proc.returncode == 0
cursor = 0
for oid, path in entries:
    end = content.index(b'\n', cursor)
    found, kind, size = content[cursor:end].split()
    assert found == oid and kind == b'blob'
    size = int(size)
    blob = content[end+1:end+1+size]
    assert hashlib.sha256(blob).digest() == hashlib.sha256((ROOT/path).read_bytes()).digest(), path
    cursor = end+size+2
assert cursor == len(content)
print(f'{len(entries)} staged skill/evidence files match verified local bytes.')
