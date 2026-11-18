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
    def test_unhashable_state_returns_error(self):
        d=copy.deepcopy(BASE);d["shots"][1]["sword_state"]=[]
        self.assertIn("shot[1]: invalid prop state: sword",validate(d))
    def test_invalid_location_type_returns_error(self):
        d=copy.deepcopy(BASE);d["shots"][1]["scabbard_location"]=[]
        self.assertIn("shot[1]: invalid prop location: sword",validate(d))
    def test_generic_non_sword_story(self):
        d=copy.deepcopy(BASE)
        for shot in d["shots"]:
            shot.pop("sword_state");shot.pop("scabbard_location")
            shot["props"]={"book":{"state":"closed","location":"desk"}}
        self.assertEqual(validate(d),[])
    def test_generic_prop_movement(self):
        d=copy.deepcopy(BASE)
        for shot in d["shots"]:
            shot.pop("sword_state");shot.pop("scabbard_location")
            shot["props"]={"book":{"state":"closed","location":"desk"}}
        d["shots"][1]["props"]["book"]["location"]="shelf"
        self.assertIn("shot[1]: unexplained prop movement: book",validate(d))
    def test_non_object_prop(self):
        d=copy.deepcopy(BASE);d["shots"][1]["props"]={"book":[]}
        self.assertIn("shot[1]: invalid prop entry",validate(d))
    def test_specific_error_code(self):
        d=copy.deepcopy(BASE);d["shots"][1]["image_file"]="S01.png"
        self.assertIn("shot[1]: duplicate image_file",validate(d))
    def test_root_array(self):
        self.assertEqual(validate([]), ["root: expected object"])
    def test_shot_array(self):
        d=copy.deepcopy(BASE);d["shots"][1]=[]
        self.assertIn("shot[1]: expected object",validate(d))
    def test_unhashable_id(self):
        d=copy.deepcopy(BASE);d["shots"][1]["id"]=[]
        self.assertIn("shot[1]: invalid id",validate(d))
    def test_unhashable_image(self):
        d=copy.deepcopy(BASE);d["shots"][1]["image_file"]=[]
        self.assertIn("shot[1]: invalid image_file",validate(d))
    def test_invalid_props_container(self):
        d=copy.deepcopy(BASE);d["shots"][1]["props"]=[]
        self.assertIn("shot[1]: invalid props",validate(d))
    def test_invalid_aspect_ratio(self):
        d=copy.deepcopy(BASE);d["aspect_ratio"]="5:4"
        self.assertIn("root: invalid aspect_ratio",validate(d))
    def test_empty_movement_action(self):
        d=copy.deepcopy(BASE);d["shots"][1]["scabbard_location"]="right_waist"
        d["shots"][1]["scabbard_move_action"]=" "
        self.assertIn("shot[1]: unexplained prop movement: sword",validate(d))
if __name__=="__main__": unittest.main()
