import json
from steps.plan.custom_fields import get_custom_fields_diff


def test_get_custom_fields_diff():
    diff = get_custom_fields_diff(target_env="qa")

    with open("custom_fields_diff_repo_vs_qa.json", "w") as fs:
        json.dump(diff, fs, indent=2)
