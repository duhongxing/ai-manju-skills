#!/usr/bin/env python3
"""Validate structured shot metadata only; does not inspect image/video pixels."""
import json, math, sys
from pathlib import Path
ALLOWED = {"sheathed":{"sheathed","partially_drawn"},"partially_drawn":{"partially_drawn","drawn","sheathed"},"drawn":{"drawn","partially_drawn"}}
def validate(data):
    if not isinstance(data,dict): return ["root must be an object"]
    shots=data.get("shots")
    if not isinstance(shots,list) or not shots: return ["shots must be a nonempty array"]
    errors=[]; ids=set(); images=set(); previous=None
    for key in ("project_id","character_id","master_version","aspect_ratio"):
        if not isinstance(data.get(key),str) or not data[key].strip(): errors.append("invalid root "+key)
    for i,s in enumerate(shots):
        if not isinstance(s,dict): errors.append("shot must be object"); previous=None; continue
        sid=s.get("id")
        if not isinstance(sid,str) or not sid.strip(): errors.append("invalid shot id")
        if sid in ids: errors.append("duplicate shot id")
        ids.add(sid)
        for key in ("character_id","master_version","scabbard_location"):
            if not isinstance(s.get(key),str) or not s[key].strip(): errors.append(str(sid)+": invalid "+key)
        for key in ("character_id","master_version"):
            if s.get(key)!=data.get(key): errors.append(str(sid)+": "+key+" mismatch")
        img=s.get("image_file")
        if not isinstance(img,str) or not img.strip(): errors.append(str(sid)+": invalid image_file")
        elif img in images: errors.append("duplicate image_file")
        else: images.add(img)
        st=s.get("sword_state")
        if st not in ALLOWED: errors.append(str(sid)+": unknown sword state")
        a,b=s.get("start"),s.get("end")
        valid=all(isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v) for v in (a,b))
        if not valid or a<0 or b<=a: errors.append(str(sid)+": invalid time")
        if previous:
            pe=previous.get("end")
            if valid and isinstance(pe,(int,float)) and not isinstance(pe,bool) and math.isfinite(pe) and abs(pe-a)>1e-6: errors.append(str(sid)+": timeline gap/overlap")
            if st not in ALLOWED.get(previous.get("sword_state"),set()): errors.append(str(sid)+": invalid sword transition")
            if s.get("scabbard_location")!=previous.get("scabbard_location") and not s.get("scabbard_move_action"): errors.append(str(sid)+": unexplained scabbard movement")
        previous=s
    return errors
if __name__=="__main__":
    errors=validate(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8")))
    print("\n".join(errors) if errors else "PASS: metadata only")
    sys.exit(bool(errors))
