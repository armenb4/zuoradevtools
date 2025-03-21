from steps.extract.custom_objects_definition import (
    extract_custom_objects_definitions_to_file,
)
from common.config.config import CUSTOM_OBJECT_NAMES


def test_extract_custom_objects_definitions():
    custom_objects_definitions = extract_custom_objects_definitions_to_file("dev")

    for object_name in CUSTOM_OBJECT_NAMES:
        assert object_name in custom_objects_definitions
