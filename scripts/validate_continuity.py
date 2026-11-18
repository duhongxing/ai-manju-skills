#!/usr/bin/env python3
"""Validate shot metadata. Does not inspect generated image or video pixels."""
import json
import math
import sys
from pathlib import Path

SWORD = {
    "sheathed": {"sheathed", "partially_drawn"},
    "partially_drawn": {"sheathed", "partially_drawn", "drawn"},
    "drawn": {"drawn", "partially_drawn"},
}

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())

def finite_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

def validate(data):
    errors = []
    if not isinstance(data, dict):
        return ["root: expected object"]
    shots = data.get("shots")
    if not isinstance(shots, list) or not shots:
        return ["shots: expected nonempty array"]
    for key in ("project_id", "character_id", "master_version"):
        if not nonempty(data.get(key)):
            errors.append("root: invalid " + key)
    if data.get("aspect_ratio") not in ("9:16", "16:9", "3:4", "1:1"):
        errors.append("root: invalid aspect_ratio")
    seen_ids, seen_images = set(), set()
    previous = None
    for index, shot in enumerate(shots):
        tag = f"shot[{index}]"
        if not isinstance(shot, dict):
            errors.append(tag + ": expected object")
            previous = None
            continue
        sid = shot.get("id")
        if not nonempty(sid):
            errors.append(tag + ": invalid id")
        elif sid in seen_ids:
            errors.append(tag + ": duplicate id")
        else:
            seen_ids.add(sid)
        for key in ("character_id", "master_version"):
            if not nonempty(shot.get(key)):
                errors.append(tag + ": invalid " + key)
            elif shot[key] != data.get(key):
                errors.append(tag + ": " + key + " mismatch")
        image = shot.get("image_file")
        if not nonempty(image):
            errors.append(tag + ": invalid image_file")
        elif image in seen_images:
            errors.append(tag + ": duplicate image_file")
        else:
            seen_images.add(image)
        start, end = shot.get("start"), shot.get("end")
        times_ok = finite_number(start) and finite_number(end)
        if not times_ok or start < 0 or end <= start:
            errors.append(tag + ": invalid time")
        props = shot.get("props", {})
        if not isinstance(props, dict):
            errors.append(tag + ": invalid props")
            props = {}
        # Backward compatibility with the original sword/scabbard fields.
        if "sword_state" in shot or "scabbard_location" in shot:
            props = dict(props)
            sword = props.setdefault("sword", {})
            if not isinstance(sword, dict):
                errors.append(tag + ": invalid sword prop")
            else:
                if "sword_state" in shot:
                    sword.setdefault("state", shot["sword_state"])
                if "scabbard_location" in shot:
                    sword.setdefault("location", shot["scabbard_location"])
                if "scabbard_move_action" in shot:
                    sword.setdefault("transition_action", shot["scabbard_move_action"])
        for pid, prop in props.items():
            if not nonempty(pid) or not isinstance(prop, dict):
                errors.append(tag + ": invalid prop entry")
                continue
            if not nonempty(prop.get("state")):
                errors.append(tag + ": invalid prop state: " + pid)
            if not nonempty(prop.get("location")):
                errors.append(tag + ": invalid prop location: " + pid)
        if previous is not None:
            old_shot, old_props = previous
            prev_end = old_shot.get("end")
            if times_ok and finite_number(prev_end) and abs(start - prev_end) > 1e-6:
                errors.append(tag + ": timeline gap/overlap")
            for pid, prop in props.items():
                if not isinstance(prop, dict) or not isinstance(old_props.get(pid), dict):
                    continue
                old = old_props[pid]
                if pid == "sword" and old.get("state") in SWORD and prop.get("state") not in SWORD[old["state"]]:
                    errors.append(tag + ": invalid sword transition")
                if old.get("location") != prop.get("location") and not nonempty(prop.get("transition_action")):
                    errors.append(tag + ": unexplained prop movement: " + pid)
        previous = (shot, props)
    return errors

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: validate_continuity.py shots.json", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
        errors = validate(data)
    except (OSError, ValueError) as exc:
        print("Input error: " + str(exc), file=sys.stderr)
        sys.exit(2)
    print("\n".join(errors) if errors else "PASS: metadata only")
    sys.exit(1 if errors else 0)
