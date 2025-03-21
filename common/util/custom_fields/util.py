import json
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.config.config import ZUORA_OBJECTS


class CustomFieldsUtil:
    @staticmethod
    def dump_custom_fields_definition(object_fields: dict, object_name: str):
        output_file = ZUORA_VCS_DIR.joinpath(f"custom_fields/{object_name}.json")
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, "w") as fs:
            json.dump(object_fields, fs, indent=2)

        logger.info(
            f"Writing {object_name} definition into file {output_file.as_posix()}"
        )

    @staticmethod
    def read_custom_fields_definition():
        all_custom_fields = {}

        for object_name in ZUORA_OBJECTS:
            object_file = ZUORA_VCS_DIR.joinpath(f"custom_fields/{object_name}.json")

            if not object_file.exists():
                continue

            with open(object_file, "r") as fs:
                object_fields: dict = json.load(fs)

            all_custom_fields[object_name] = object_fields

        return all_custom_fields

    @staticmethod
    def diff(source_objects: dict, target_objects: dict) -> dict:
        all_diffs = {}

        for object_name in ZUORA_OBJECTS:
            diff = {
                "add": {},
                "delete": {},
                "update": {},
            }

            source_object: dict[str, dict] = source_objects[object_name]
            target_object: dict[str, dict] = target_objects[object_name]

            for field_name, field_definition in source_object["custom_fields"].items():
                if field_name not in target_object["custom_fields"]:
                    diff["add"][field_name] = field_definition
                    continue

                # try:
                #     field_definition.pop("description")
                # except KeyError:
                #     pass

                # try:
                #     target_object["custom_fields"][field_name].pop("description")
                # except KeyError:
                #     pass

                # try:
                #     field_definition.pop("displayName")
                # except KeyError:
                #     pass

                # try:
                #     target_object["custom_fields"][field_name].pop("displayName")
                # except KeyError:
                #     pass

                # try:
                #     field_definition.pop("default")
                # except KeyError:
                #     pass

                # try:
                #     target_object["custom_fields"][field_name].pop("default")
                # except KeyError:
                #     pass

                # try:
                #     field_definition.pop("enum")
                # except KeyError:
                #     pass

                # try:
                #     target_object["custom_fields"][field_name].pop("enum")
                # except KeyError:
                #     pass

                if field_definition != target_object["custom_fields"][field_name]:
                    diff["update"][field_name] = {
                        "old": target_object["custom_fields"][field_name],
                        "new": field_definition,
                    }

            for field_name, field_definition in target_object["custom_fields"].items():
                if field_name not in source_object["custom_fields"]:
                    diff["delete"][field_name] = field_definition

            all_diffs[object_name] = diff

        return all_diffs
