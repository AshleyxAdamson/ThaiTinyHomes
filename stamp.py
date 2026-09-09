#!/usr/bin/env python3
"""Content-hash assets and rewrite references in index.html / styles.css.

Run in REPO after each rsync from the prototype (which uses unhashed names):
    rsync -a --delete --exclude .DS_Store --exclude README.md \
        "<prototype>/index.html" "<prototype>/styles.css" "<prototype>/main.js" \
        "<prototype>/build-artifact.py" "<prototype>/assets" .
    python3 stamp.py

For each file under assets/img, assets/video, assets/fonts, renames it to
name.<8-hex-sha256>.ext and repoints every src / srcset / poster / data-src /
href / og:image / CSS url(...) reference in index.html and styles.css. A file
already named with its current content hash is left alone, so re-running is a
no-op (idempotent).

stdlib only.
"""
import hashlib
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
ASSET_DIRS = ["assets/img", "assets/video", "assets/fonts"]
TEXT_FILES = ["index.html", "styles.css"]

# name.<8 hex>.ext  -- an already-hashed filename
HASHED_RE = re.compile(r'^(?P<base>.+)\.(?P<hash>[0-9a-f]{8})\.(?P<ext>[^.]+)$')
# any reference under assets/{img,video,fonts}/... found in html/css text
ASSET_REF_RE = re.compile(r'assets/(?:img|video|fonts)/[A-Za-z0-9_.-]+')


def sha256_prefix(path: Path, n: int = 8) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


def split_name(filename: str):
    """Return (base_without_hash, ext) for a possibly-already-hashed filename."""
    m = HASHED_RE.match(filename)
    if m:
        return m.group("base"), m.group("ext")
    if "." in filename:
        base, ext = filename.rsplit(".", 1)
        return base, ext
    return filename, ""


def stamp_assets():
    """Rename files in place; return dict of canonical unhashed key ->
    current hashed relative path, plus the list of (old, new) renames."""
    key_to_new = {}
    renames = []
    for d in ASSET_DIRS:
        dir_path = REPO / d
        if not dir_path.is_dir():
            continue
        for entry in sorted(dir_path.iterdir(), key=lambda p: p.name):
            if not entry.is_file():
                continue
            base, ext = split_name(entry.name)
            new_hash = sha256_prefix(entry)
            key = f"{d}/{base}.{ext}"
            current_hash_match = HASHED_RE.match(entry.name)
            current_hash = current_hash_match.group("hash") if current_hash_match else None

            if current_hash == new_hash:
                key_to_new[key] = f"{d}/{entry.name}"
                continue

            new_name = f"{base}.{new_hash}.{ext}"
            new_path = dir_path / new_name
            old_rel = f"{d}/{entry.name}"
            new_rel = f"{d}/{new_name}"
            entry.rename(new_path)
            key_to_new[key] = new_rel
            renames.append((old_rel, new_rel))
    return key_to_new, renames


def rewrite_refs(text: str, key_to_new: dict):
    changed = []

    def repl(m):
        ref = m.group(0)
        dirpart, filename = ref.rsplit("/", 1)
        base, ext = split_name(filename)
        key = f"{dirpart}/{base}.{ext}"
        new_ref = key_to_new.get(key)
        if new_ref is None or new_ref == ref:
            return ref
        changed.append((ref, new_ref))
        return new_ref

    new_text = ASSET_REF_RE.sub(repl, text)
    return new_text, changed


def main():
    key_to_new, renames = stamp_assets()

    all_ref_changes = []
    for fname in TEXT_FILES:
        path = REPO / fname
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        new_text, changed = rewrite_refs(text, key_to_new)
        if changed:
            path.write_text(new_text, encoding="utf-8")
        for old, new in changed:
            all_ref_changes.append((fname, old, new))

    if renames:
        print(f"Renamed {len(renames)} asset file(s):")
        width = max(len(old) for old, _ in renames)
        for old, new in renames:
            print(f"  {old.ljust(width)}  ->  {new}")
    else:
        print("No asset renames needed (content unchanged).")

    if all_ref_changes:
        print(f"\nUpdated {len(all_ref_changes)} reference(s):")
        for fname, old, new in all_ref_changes:
            print(f"  {fname}: {old}  ->  {new}")
    else:
        print("No references needed updating.")


if __name__ == "__main__":
    sys.exit(main())
