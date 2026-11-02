"""Verify bundled content using the same Python minor version as the APK."""
import hashlib
import io
import json
import marshal
from pathlib import Path
import sys
import tarfile
import zipfile

root = Path(__file__).resolve().parents[1]
apk = Path(sys.argv[1])
with zipfile.ZipFile(apk) as archive:
    assert archive.testzip() is None
    with tarfile.open(fileobj=io.BytesIO(archive.read('assets/private.tar'))) as bundle:
        files = {entry.name: bundle.extractfile(entry).read() for entry in bundle if entry.isfile()}
manifest = json.loads((root / 'tests/content.sha256.json').read_text(encoding='utf8'))
for name, expected in manifest.items():
    assert hashlib.sha256(files[name]).hexdigest() == expected, name
assert not any(name.startswith(('data/progress/', 'state/', 'tests/', 'artifacts/')) for name in files)
assert files['app.kv'] == (root / 'app.kv').read_bytes()
source_files = [root / 'main.py', *sorted((root / 'screens').glob('*.py')), *sorted((root / 'utils').glob('*.py'))]
for path in source_files:
    name = path.relative_to(root).as_posix() + 'c'
    bytecode = files[name]
    import importlib.util
    assert bytecode[:4] == importlib.util.MAGIC_NUMBER, 'Use the APK build host Python (3.11) for bytecode verification'
    actual = marshal.loads(bytecode[16:])
    source = path.read_text(encoding='utf8')
    assert any(actual == compile(source, actual.co_filename, 'exec', optimize=level) for level in (0, 1, 2)), name
print(json.dumps({'apk': apk.name, 'sha256': hashlib.sha256(apk.read_bytes()).hexdigest(),
                  'protected_assets': len(manifest), 'source_modules': len(source_files),
                  'user_state_bundled': False}, indent=2))
