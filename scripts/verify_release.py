"""Verify the approved source and font files. Uses Python's standard library."""
from hashlib import sha256
import json
from pathlib import Path


def verify(root):
    manifest = json.loads((root / "release.json").read_text())
    entries = manifest["sha256"]
    if not entries:
        raise ValueError("Release manifest is empty")
    for relative, expected in entries.items():
        path = (root / relative).resolve()
        if not path.is_relative_to(root.resolve()):
            raise ValueError(f"Path outside repository: {relative}")
        actual = sha256(path.read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Checksum mismatch: {relative}")
        print(f"OK {relative}")
    print(f"Verified {len(entries)} release files.")


if __name__ == "__main__":
    verify(Path(__file__).resolve().parents[1])
