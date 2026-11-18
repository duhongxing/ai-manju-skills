import copy, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"scripts"))
from validate_continuity import validate
BASE=json.loads((ROOT/"examples/mie-men-zhi-ye/shots.json").read_text(encoding="utf-8"))
class ContinuityTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(validate(BASE),[])
    def test_duplicate_image(self):
        d=copy.deepcopy(BASE);d["shots"][1]["image_file"]="S01.png";self.assertTrue(validate(d))
    def test_character_mismatch(self):
        d=copy.deepcopy(BASE);d["shots"][1]["character_id"]="other";self.assertTrue(validate(d))
    def test_invalid_transition(self):
        d=copy.deepcopy(BASE);d["shots"][1]["sword_state"]="drawn";d["shots"][2]["sword_state"]="sheathed";self.assertTrue(validate(d))
    def test_gap(self):
        d=copy.deepcopy(BASE);d["shots"][1]["start"]=4;self.assertTrue(validate(d))
    def test_duplicate_id(self):
        d=copy.deepcopy(BASE);d["shots"][1]["id"]="S01";self.assertTrue(validate(d))
    def test_missing_image(self):
        d=copy.deepcopy(BASE);d["shots"][1]["image_file"]="";self.assertTrue(validate(d))
    def test_unexplained_move(self):
        d=copy.deepcopy(BASE);d["shots"][1]["scabbard_location"]="right_waist";self.assertTrue(validate(d))
    def test_declared_move(self):
        d=copy.deepcopy(BASE);d["shots"][1]["scabbard_location"]="right_waist";d["shots"][1]["scabbard_move_action"]="move scabbard";d["shots"][2]["scabbard_location"]="right_waist";self.assertEqual(validate(d),[])
    def test_boolean_time(self):
        d=copy.deepcopy(BASE);d["shots"][0]["start"]=True;self.assertTrue(validate(d))
    def test_negative_duration(self):
        d=copy.deepcopy(BASE);d["shots"][1]["end"]=2;self.assertTrue(validate(d))
    def test_unknown_state(self):
        d=copy.deepcopy(BASE);d["shots"][1]["sword_state"]="floating";self.assertTrue(validate(d))
if __name__=="__main__": unittest.main()
