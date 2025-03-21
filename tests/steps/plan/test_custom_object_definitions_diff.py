import json
from steps.plan.custom_objects_definition import get_custom_objects_definitions_diff


def test_get_custom_objects_definitions_diff():
    diff = get_custom_objects_definitions_diff(target_env="qa")

    with open("custom_objects_definitions_diff_repo_vs_qa.json", "w") as fs:
        json.dump(diff, fs, indent=2)
