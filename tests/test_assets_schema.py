import copy
import json
import unittest
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT=Path(__file__).resolve().parents[1]/"schemas"
def validator(name):
    schema=json.loads((ROOT/name).read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)

CHAR=validator("character.schema.json")
PROP=validator("prop-state.schema.json")
CHARACTER={"character_id":"SC-LI-001","master_version":"v1","dna":{"age":22},"views":{"front":"front.png","side":"side.png","back":"back.png"}}
ITEM={"prop_id":"sword-1","state":"sheathed","location":"left_waist"}

class AssetSchemaTests(unittest.TestCase):
    def test_character_valid(self): self.assertTrue(CHAR.is_valid(CHARACTER))
    def test_prop_valid(self): self.assertTrue(PROP.is_valid(ITEM))
    def test_character_requires_three_views(self):
        d=copy.deepcopy(CHARACTER);del d["views"]["side"]
        self.assertFalse(CHAR.is_valid(d))
    def test_character_rejects_blank_master(self):
        d=copy.deepcopy(CHARACTER);d["master_version"]="  "
        self.assertFalse(CHAR.is_valid(d))
    def test_character_requires_dna(self):
        d=copy.deepcopy(CHARACTER);d["dna"]={}
        self.assertFalse(CHAR.is_valid(d))
    def test_prop_rejects_blank_location(self):
        d=copy.deepcopy(ITEM);d["location"]=" "
        self.assertFalse(PROP.is_valid(d))
    def test_prop_rejects_blank_action(self):
        d=copy.deepcopy(ITEM);d["transition_action"]=" "
        self.assertFalse(PROP.is_valid(d))
if __name__=="__main__": unittest.main()
