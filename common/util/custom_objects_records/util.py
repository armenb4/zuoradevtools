import json
from typing import List
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR


class CustomObjectRecordsUtil:
    @staticmethod
    def remove_key_from_dict(obj: dict, key: str):
        try:
            obj.pop(key)
        except Exception:
            pass

    @staticmethod
    def remove_keys_from_dict(obj: dict, keys: List[str]):
        for key in keys:
            CustomObjectRecordsUtil.remove_key_from_dict(obj, key)

    @staticmethod
    def dump_records_to_file(records: List[dict], object_name: str):
        output_file = ZUORA_VCS_DIR.joinpath(
            f"custom_object_records/{object_name}.json"
        )
        output_file.parent.mkdir(exist_ok=True, parents=True)
        logger.info(f"Writing {object_name} records into file {output_file.as_posix()}")

        with open(output_file, "w") as fs:
            json.dump(records, fs, indent=2)

    @staticmethod
    def read_custom_object_record() -> dict:
        logger.info("🟡 Reading custom object records from Zuora-VCS repository")
        custom_object_records = {}
        custom_object_records_dir = ZUORA_VCS_DIR.joinpath("custom_object_records")
        files = list(custom_object_records_dir.glob("*.json"))
        for file in files:
            with open(file) as fs:
                records = json.load(fs)

            custom_object_records[file.stem] = records

        logger.info(
            "✅ Reading custom object records from Zuora-VCS repository finished"
        )
        return custom_object_records
