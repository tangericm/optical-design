"""Recheck retained local full-release receipts and freeze implementation hashes."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT/'skills/optical-design/scripts'))
from _lib.review_report import validate_review_receipt


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    records = {}
    paths = [HERE/f'composite-{engine}/report.json' for engine in ['zos', 'optiland']]
    summary = json.loads((HERE/'mcp-results.json').read_text())
    paths.extend(Path(item['report']) for item in summary.values())
    paths.extend(HERE/f'final-composite/composite-{engine}/report.json' for engine in ['zos', 'optiland'])
    final_summary = json.loads((HERE/'final-mcp/mcp-results.json').read_text())
    paths.extend(Path(item['report']) for item in final_summary.values())
    for path in paths:
        report = json.loads(path.read_text())
        metadata = validate_review_receipt(path)
        source = Path(report['source']['path'])
        assert sha(source) == report['source']['sha256']
        assert report['source_unchanged'] and report['baseline_restored']
        records[str(path.relative_to(HERE))] = metadata
    shape = json.loads((HERE/'shape-fixtures.json').read_text())
    for item in shape.values():
        assert sha(Path(item['model'])) == item['sha256']
        assert all(abs(p['analytic_sag_mm']-p['native_sag_mm']) < 1e-12 for p in item['sag_anchors'])
    installed = json.loads((HERE/'installed-release.json').read_text())
    assert installed['status'] == 'passed'
    files = list((ROOT/'skills/optical-design/scripts').rglob('*.py'))
    files += [ROOT/'skills/optical-design/SKILL.md', ROOT/'package.json']
    result = {'schema': '1', 'verified_receipts': records,
              'implementation_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sorted(files)},
              'native_shape_fixture_sha256': sha(HERE/'shape-fixtures.json'),
              'installed_release_sha256': sha(HERE/'installed-release.json'),
              'scope': 'retained local receipt/byte validation; not a fresh optical run or physical certification'}
    (HERE/'verified-evidence.json').write_bytes((json.dumps(result, indent=2)+'\n').encode())
    print(f'Verified {len(records)} receipts, two shape fixtures and {len(files)} implementation files.')


if __name__ == '__main__':
    main()
