import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_character import validate_character

BASE = {
    "character_id": "SC-LI-001",
    "master_version": "v1",
    "master_file": "master.png",
    "views": {"front": "front.png", "side": "side.png", "back": "back.png"},
}

class CharacterTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(validate_character(BASE), [])
    def test_duplicate_views(self):
        d=copy.deepcopy(BASE);d["views"]["back"]="front.png"
        self.assertIn("character: duplicate image reference back and front", validate_character(d))
    def test_master_reused_as_view(self):
        d=copy.deepcopy(BASE);d["views"]["front"]="master.png"
        self.assertIn("character: duplicate image reference front and master_file", validate_character(d))
    def test_missing_view(self):
        d=copy.deepcopy(BASE);d["views"].pop("side")
        self.assertIn("character: invalid view side", validate_character(d))
    def test_non_object_views(self):
        d=copy.deepcopy(BASE);d["views"]=[]
        self.assertIn("character: invalid views", validate_character(d))
    def test_current_approved_record(self):
        d=copy.deepcopy(BASE)
        d["generation_records"]=[{"asset_file":"front.png","master_version":"v1","status":"approved"}]
        self.assertEqual(validate_character(d),[])
    def test_stale_approved_record(self):
        d=copy.deepcopy(BASE)
        d["generation_records"]=[{"asset_file":"front.png","master_version":"v0","status":"approved"}]
        self.assertIn("record[0]: stale approved asset",validate_character(d))
    def test_old_pending_record_allowed(self):
        d=copy.deepcopy(BASE)
        d["generation_records"]=[{"asset_file":"front.png","master_version":"v0","status":"review_pending"}]
        self.assertEqual(validate_character(d),[])
    def test_unreferenced_asset_record(self):
        d=copy.deepcopy(BASE)
        d["generation_records"]=[{"asset_file":"unknown.png","master_version":"v1","status":"approved"}]
        self.assertIn("record[0]: unreferenced asset_file",validate_character(d))
if __name__ == "__main__":
    unittest.main()
