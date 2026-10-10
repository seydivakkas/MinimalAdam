#!/usr/bin/env python3
"""Create and independently verify reproducible MinimalAdam release assets.

The ZIP includes exactly the tracked source files plus a freshly generated
RELEASE_MANIFEST.json. No packaged font binaries, credentials, or Git metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import zipfile
from pathlib import Path

PRODUCT = "MinimalAdam"
BLOCKED_PARTS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "outputs"}
REQUIRED = {"README.md", "LICENSE", "NOTICE.md", "ACCEPTANCE.md", "MinimalAdam-Studio.cmd",
            "editor/offline.html", "minimaladam/SKILL.md", "docs/RELEASE_NOTES_v0.6.1.md"}
ZIP_TIME = (2026, 1, 1, 0, 0, 0)


def sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()


def collect(root: Path) -> dict[str, bytes]:
    if (root / ".git").exists():
        names = subprocess.check_output(["git", "ls-files", "-z"], cwd=root).split(b"\x00")
        paths = [Path(v.decode("utf-8")) for v in names if v]
    else:
        paths = [p.relative_to(root) for p in root.rglob("*") if p.is_file()]
    files = {}
    for rel in paths:
        if (not rel.parts or any(part in BLOCKED_PARTS for part in rel.parts)
                or rel.name == "RELEASE_MANIFEST.json" or rel.suffix in {".pyc", ".pyo"}):
            continue
        if rel.is_absolute() or ".." in rel.parts or "\\" in rel.as_posix():
            raise ValueError(f"Unsafe source path: {rel}")
        if rel.name == ".env" or rel.name.startswith(".env.") or rel.suffix in {".key", ".pem", ".p12"}:
            raise ValueError(f"Potential secret in release: {rel}")
        full = root / rel
        if full.is_symlink():
            raise ValueError(f"Symlink not allowed in release: {rel}")
        files[rel.as_posix()] = full.read_bytes()
    if not REQUIRED.issubset(files):
        raise ValueError(f"Missing mandatory release files: {sorted(REQUIRED - files.keys())}")
    return dict(sorted(files.items()))


def put(zf: zipfile.ZipFile, path: str, data: bytes) -> None:
    zi = zipfile.ZipInfo(path, date_time=ZIP_TIME)
    zi.compress_type = zipfile.ZIP_DEFLATED
    zi.create_system = 3
    zi.external_attr = 0o100644 << 16
    zf.writestr(zi, data, compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)


def build(root: Path, out: Path, version: str, commit: str, ci_url: str) -> list[Path]:
    if version != "0.6.1":
        raise ValueError("This release contract applies only to v0.6.1")
    if len(commit) != 40 or any(x not in "0123456789abcdef" for x in commit):
        raise ValueError("Source commit must be a full lowercase Git SHA")
    files = collect(root)
    manifest = {
        "product": PRODUCT,
        "version": version,
        "source_repository": "https://github.com/seydivakkas/MinimalAdam",
        "source_commit": commit,
        "ci_evidence": ci_url,
        "license": "MIT; upstream author attribution preserved in NOTICE.md",
        "acceptance": "Windows Python 3.12/3.14 CI passed; six user-reported desktop checks passed",
        "checksums": "SHA-256",
        "file_count": len(files),
        "files": {name: {"bytes": len(data), "sha256": sha256(data)} for name, data in files.items()},
    }
    manifest_bytes = (json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    out.mkdir(parents=True, exist_ok=True)
    archive = out / f"{PRODUCT}-v{version}.zip"
    external_manifest = out / f"{PRODUCT}-v{version}.manifest.json"
    checksums = out / "SHA256SUMS.txt"
    with zipfile.ZipFile(archive, "w") as zf:
        for name, data in files.items():
            put(zf, f"{PRODUCT}/{name}", data)
        put(zf, f"{PRODUCT}/RELEASE_MANIFEST.json", manifest_bytes)
    external_manifest.write_bytes(manifest_bytes)
    checksums.write_text(
        f"{sha256(archive.read_bytes())}  {archive.name}\n"
        f"{sha256(manifest_bytes)}  {external_manifest.name}\n", encoding="utf-8"
    )
    verify(archive, external_manifest, checksums)
    return [archive, external_manifest, checksums]


def verify(archive: Path, external_manifest: Path, checksums: Path) -> None:
    manifest_bytes = external_manifest.read_bytes()
    manifest = json.loads(manifest_bytes)
    with zipfile.ZipFile(archive, "r") as zf:
        if zf.testzip() is not None:
            raise ValueError("Damaged ZIP entry")
        expected = {f"{PRODUCT}/{x}" for x in manifest["files"]}
        expected.add(f"{PRODUCT}/RELEASE_MANIFEST.json")
        if set(zf.namelist()) != expected:
            raise ValueError("Release ZIP has missing or extra files")
        if zf.read(f"{PRODUCT}/RELEASE_MANIFEST.json") != manifest_bytes:
            raise ValueError("Manifest inside ZIP differs")
        for path, meta in manifest["files"].items():
            data = zf.read(f"{PRODUCT}/{path}")
            if len(data) != meta["bytes"] or sha256(data) != meta["sha256"]:
                raise ValueError(f"SHA-256 mismatch: {path}")
    entries = [line.split("  ", 1) for line in checksums.read_text(encoding="utf-8").splitlines()]
    expected_sums = {archive.name: sha256(archive.read_bytes()),
                     external_manifest.name: sha256(manifest_bytes)}
    if len(entries) != 2 or any(expected_sums.get(name) != digest for digest, name in entries):
        raise ValueError("SHA256SUMS.txt does not match release assets")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output-dir", type=Path, default=Path("dist"))
    parser.add_argument("--version", default="0.6.1")
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--ci-url", required=True)
    args = parser.parse_args()
    paths = build(args.root.resolve(), args.output_dir.resolve(), args.version, args.source_commit, args.ci_url)
    print(f"PASS: {len(paths)} release assets; full source and manifest SHA-256 checked.")
    for path in paths:
        print(f"{path.name}: {len(path.read_bytes())} bytes; SHA-256 {sha256(path.read_bytes())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
