import json
import copy
from typing import List, Dict
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR, CUSTOM_OBJECT_NAMES, CUSTOM_OBJECTS_MAP
from common.util.custom_objects_records import CustomObjectRecordsUtil
from steps.extract.custom_object_records import extract_custom_object_records


def get_custom_objects_records_diff(target_env: str) -> dict:
    logger.info("Getting all custom objects records difference")
    diff = {}

    source_records = CustomObjectRecordsUtil.read_custom_object_record()
    target_records = extract_custom_object_records(
        environment=target_env,
        custom_object_names=CUSTOM_OBJECT_NAMES,
        remove_keys=False,
    )
    target_record_names = list(target_records.keys())
    for custom_object_type, criteria in CUSTOM_OBJECTS_MAP.items():
        if custom_object_type not in target_record_names:
            continue

        # Checking difference for each item in custom object key map
        custom_object_diff = get_single_custom_object_records_diff(
            object_type=custom_object_type,
            criteria=criteria,
            records_source_env=source_records[custom_object_type],
            records_target_env=target_records[custom_object_type],
        )

        diff[custom_object_type] = custom_object_diff

    if not diff:
        return None

    output_dir = ZUORA_VCS_DIR.joinpath("temp/custom_object_records")
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir.joinpath("diff.json")

    logger.info("Writing custom objects records diff into file...")
    logger.info(f"🟢  {output_file.as_posix()}")
    with open(output_file, "w") as fs:
        json.dump(diff, fs, indent=4)

    return diff


def get_single_custom_object_records_diff(
    object_type: str,
    criteria: dict,
    records_source_env: List[dict],
    records_target_env: List[dict],
):
    logger.info(f"Comparing {object_type} records ...")
    if object_type not in CUSTOM_OBJECTS_MAP.keys():
        raise ValueError(f"Not a valid object type - {object_type}")

    add_records = []
    edit_records = []
    delete_records = []

    # Finding records to add or edit
    for record_source_env in records_source_env:
        matching_record = find_match(records_target_env, record_source_env, criteria)
        if matching_record:
            # Special custom object conditions
            if "LookupType__c" in record_source_env:
                if record_source_env["LookupType__c"] == "SEQUENCESET":
                    continue

            temp = {}
            for key, source_value in record_source_env.items():
                if key in ("Id"):
                    continue

                if matching_record.get(key) != source_value:
                    logger.info(f"Source and destination values do not match for {key}")
                    logger.info(f"{matching_record.get(key)} =/= {source_value}")
                    temp[key] = source_value
                    temp["__" + key] = matching_record.get(key)
                    temp["Id"] = matching_record["Id"]
            if temp:
                edit_records.append(temp)
        else:
            temp = copy.deepcopy(record_source_env)
            try:
                temp.pop("Id")
            except KeyError:
                pass

            # Special custom object conditions
            if "LookupType__c" in record_source_env:
                if record_source_env["LookupType__c"] == "SEQUENCESET":
                    temp["LookupValue1__c"] = "To be generated on DEPLOY step"

            add_records.append(temp)

    # Finding records to delete
    for record_target_env in records_target_env:
        matching_record = find_match(records_source_env, record_target_env, criteria)
        if not matching_record:
            delete_records.append(record_target_env)

    return {
        "add": add_records,
        "edit": edit_records,
        "delete": delete_records,
    }


def find_match(records: List[Dict], compare_record: Dict, criteria: Dict):
    primary_key = criteria["primary"]
    secondary_key = criteria.get("secondary")

    for record in records:
        if record.get(primary_key) == compare_record.get(primary_key):
            if not secondary_key:
                return record

            if record.get(secondary_key) == compare_record.get(secondary_key):
                return record
    return None
