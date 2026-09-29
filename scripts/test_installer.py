"""Offline installer checks; uses a temporary home and mocked downloads."""
from hashlib import sha256
import os
from pathlib import Path
import subprocess
import tempfile

script = Path(__file__).with_name("vina-font").resolve()
with tempfile.TemporaryDirectory() as directory:
    root = Path(directory)
    bin_dir = root / "bin"
    bin_dir.mkdir()
    payload = b"\x00\x01\x00\x00test-font"
    (root / "font").write_bytes(payload)
    sums = root / "sums"
    sums.write_text(sha256(payload).hexdigest() + "  VinaEpKim-VF.ttf\n")
    mocks = {
        "uname": '#!/bin/sh\necho Darwin\n',
        "curl": '''#!/bin/bash
while [[ $# -gt 0 ]]; do
 case "$1" in
  https:*) url=$1; shift ;;
  -o) out=$2; shift 2 ;;
  *) shift ;;
 esac
done
case "$url" in
 */SHA256SUMS) cp "$FIXTURE/sums" "$out" ;;
 *) cp "$FIXTURE/font" "$out" ;;
esac
''',
    }
    for name, content in mocks.items():
        path = bin_dir / name
        path.write_text(content)
        path.chmod(0o755)
    env = {**os.environ, "HOME": str(root), "FIXTURE": str(root),
           "PATH": str(bin_dir) + os.pathsep + os.environ["PATH"]}
    def run(*args):
        return subprocess.run(["bash", str(script), *args], env=env,
                              capture_output=True, text=True)
    target = root / "Library/Fonts/VinaEpKim-VF.ttf"
    target.parent.mkdir(parents=True)
    target.write_bytes(b"previous-font")
    sums.write_text("0" * 64 + "  VinaEpKim-VF.ttf\n")
    assert run("update").returncode != 0
    assert target.read_bytes() == b"previous-font"
    sums.write_text(sha256(payload).hexdigest() + "  VinaEpKim-VF.ttf\n")
    result = run("install")
    assert result.returncode == 0, result.stderr
    assert target.read_bytes() == payload
    backups = list((root / "Library/Application Support/VinaEpKim/backups").glob("*.ttf"))
    assert len(backups) == 1 and backups[0].read_bytes() == b"previous-font"
    assert "already up to date" in run("update").stdout
    assert run("install", "../invalid").returncode != 0
    assert "Installed:" in run("status").stdout
print("Installer checks passed: checksum rejection, backup, install, no-op update, status, invalid repository.")
