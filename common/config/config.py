import json
from pathlib import Path

_root_dir = Path(__file__).parent.parent.parent

ZUORA_VCS_DIR = _root_dir.parent.joinpath("zuora-vcs")


with open(_root_dir.joinpath("config.json")) as fs:
    config = json.load(fs)


CUSTOM_OBJECT_NAMES = config["CUSTOM_OBJECT_NAMES"]
CUSTOM_OBJECTS_MAP = config["CUSTOM_OBJECTS_MAP"]
WORKFLOW_NAMES = config["WORKFLOW_NAMES"]
ZUORA_OBJECTS = config["ZUORA_OBJECTS"]
