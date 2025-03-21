import json
from common.util.custom_objects_definitions import CustomObjectsDefinitionUtil


def test_diff_custom_fields():
    all_diffs = CustomObjectsDefinitionUtil.diff("dev", "qa")

    with open("all_custom_object_definitions_diffs.json", "w") as fs:
        json.dump(all_diffs, fs, indent=2)
