#!/usr/bin/env python3
"""Check character asset references; does not verify actual image contents."""
import json
import sys
from pathlib import Path

def validate_character(data):
    if not isinstance(data, dict):
        return ["character: expected object"]
    errors = []
    files = []
    for key in ("character_id", "master_version", "master_file"):
        v = data.get(key)
        if not isinstance(v, str) or not v.strip():
            errors.append("character: invalid " + key)
    master = data.get("master_file")
    if isinstance(master, str) and master.strip():
        files.append(("master_file", master.strip()))
    views = data.get("views")
    if not isinstance(views, dict):
        errors.append("character: invalid views")
        return errors
    for key in ("front", "side", "back"):
        v = views.get(key)
        if not isinstance(v, str) or not v.strip():
            errors.append("character: invalid view " + key)
        else:
            files.append((key, v.strip()))
    seen = {}
    for key, name in files:
        if name in seen:
            errors.append("character: duplicate image reference " + key + " and " + seen[name])
        else:
            seen[name] = key
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_character.py character.json", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print("Input error: " + str(exc), file=sys.stderr)
        sys.exit(2)
    errors = validate_character(data)
    print("\n".join(errors) if errors else "PASS: references only")
    sys.exit(bool(errors))
