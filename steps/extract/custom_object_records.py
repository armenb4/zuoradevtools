import copy
from typing import List
from common.app.zuora.api import ZuoraAPI
from common.lib.logger import logger
from common.util.custom_objects_records import CustomObjectRecordsUtil

KEYS_TO_REMOVE = [
    "Id",
    "type",
    "CreatedById",
    "UpdatedById",
    "CreatedDate",
    "UpdatedDate",
]


def extract_custom_object_records(
    environment: str,
    custom_object_names: List[str],
    remove_keys: bool = False,
) -> dict:
    logger.info(
        f"🟡 Extracting custom object records from Zuora environment {environment.upper()}"
    )

    zuora_api = ZuoraAPI(environment)

    custom_object_records = {}
    for custom_object_name in custom_object_names:
        records_url = f"objects/records/default/{custom_object_name}"
        logger.info(f"Get request to {records_url}")
        response = zuora_api.get(records_url)
        if response.status_code == 200:
            response_json = response.json()
            records: List[dict] = response_json["records"]

            copied_records = copy.deepcopy(records)
            if remove_keys:
                for record in copied_records:
                    CustomObjectRecordsUtil.remove_keys_from_dict(
                        record, KEYS_TO_REMOVE
                    )

            custom_object_records[custom_object_name] = copied_records
    return custom_object_records


def extract_custom_object_records_to_file(
    environment: str,
    custom_object_names: List[str],
    remove_keys: bool = False,
) -> dict:
    custom_object_records = extract_custom_object_records(
        environment=environment,
        custom_object_names=custom_object_names,
        remove_keys=remove_keys,
    )
    for custom_object_name, records in custom_object_records.items():
        CustomObjectRecordsUtil.dump_records_to_file(records, custom_object_name)
