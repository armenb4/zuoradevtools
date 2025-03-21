import json
from typing import List
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.config.config import CUSTOM_OBJECT_NAMES


class CustomObjectsDefinitionUtil:
    @staticmethod
    def remove_key_from_dict(obj: dict, key: str):
        try:
            obj.pop(key)
        except Exception:
            pass

    @staticmethod
    def remove_keys_from_dict(obj: dict, keys: List[str]):
        for key in keys:
            CustomObjectsDefinitionUtil.remove_key_from_dict(obj, key)

    @staticmethod
    def dump_object_definition(object_fields: dict, object_name: str):
        output_file = ZUORA_VCS_DIR.joinpath(f"custom_objects/{object_name}.json")
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, "w") as fs:
            json.dump(object_fields, fs, indent=2)

        logger.info(
            f"Writing {object_name} definition into file {output_file.as_posix()}"
        )

    @staticmethod
    def read_custom_objects_definition():
        all_custom_objects = {}

        for object_name in CUSTOM_OBJECT_NAMES:
            object_file = ZUORA_VCS_DIR.joinpath(f"custom_objects/{object_name}.json")

            if not object_file.exists():
                continue

            with open(object_file, "r") as fs:
                object_fields: dict = json.load(fs)

            all_custom_objects[object_name] = object_fields

        return all_custom_objects

    @staticmethod
    def diff(source_definitions: dict, target_definitions: dict) -> dict:
        all_diffs = {}

        for object_name in CUSTOM_OBJECT_NAMES:
            diff = {
                "add": {},
                "delete": {},
                "update": {},
            }
            source_object: dict[str, dict] = source_definitions[object_name]["schema"]
            target_object: dict[str, dict] = target_definitions[object_name]["schema"]

            for field_name, field_definition in source_object["properties"].items():
                if field_name not in target_object["properties"]:
                    diff["add"][field_name] = field_definition
                    continue

                if field_definition != target_object["properties"][field_name]:
                    diff["update"][field_name] = {
                        "old": target_object["properties"][field_name],
                        "new": field_definition,
                    }

            for field_name, field_definition in target_object["properties"].items():
                if field_name not in source_object["properties"]:
                    diff["delete"][field_name] = field_definition

            all_diffs[object_name] = diff

        return all_diffs
