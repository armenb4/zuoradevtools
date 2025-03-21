import json
from common.util.custom_fields.util import CustomFieldsUtil


def test_diff_custom_fields():
    all_diffs = CustomFieldsUtil.diff("qa", "uat")

    with open("all_custom_fields_diffs.json", "w") as fs:
        json.dump(all_diffs, fs, indent=2)
