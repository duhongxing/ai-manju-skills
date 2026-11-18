import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((ROOT / "schemas/shot.schema.json").read_text(encoding="utf-8"))
SAMPLE = json.loads((ROOT / "examples/mie-men-zhi-ye/shots.json").read_text(encoding="utf-8"))
VALIDATOR = Draft202012Validator(SCHEMA)

class ShotSchemaTests(unittest.TestCase):
    def test_schema_valid(self):
        Draft202012Validator.check_schema(SCHEMA)
    def test_sample_valid(self):
        self.assertEqual(list(VALIDATOR.iter_errors(SAMPLE)), [])
    def test_no_sword_required_for_generic_story(self):
        d=copy.deepcopy(SAMPLE)
        for shot in d["shots"]:
            shot.pop("sword_state");shot.pop("scabbard_location")
            shot["props"]={"book":{"state":"closed","location":"desk"}}
        self.assertEqual(list(VALIDATOR.iter_errors(d)), [])
    def test_missing_image_rejected(self):
        d=copy.deepcopy(SAMPLE);d["shots"][0].pop("image_file")
        self.assertTrue(list(VALIDATOR.iter_errors(d)))
    def test_invalid_prop_type_rejected(self):
        d=copy.deepcopy(SAMPLE);d["shots"][0]["props"]={"book":[]}
        self.assertTrue(list(VALIDATOR.iter_errors(d)))
    def test_invalid_aspect_rejected(self):
        d=copy.deepcopy(SAMPLE);d["aspect_ratio"]="5:4"
        self.assertTrue(list(VALIDATOR.iter_errors(d)))
    def test_blank_character_rejected(self):
        d=copy.deepcopy(SAMPLE);d["character_id"]=""
        self.assertTrue(list(VALIDATOR.iter_errors(d)))
if __name__ == "__main__":
    unittest.main()
