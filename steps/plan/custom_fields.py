import json
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from steps.extract.custom_fields import extract_custom_fields
from common.util.custom_fields.util import CustomFieldsUtil


def get_custom_fields_diff(
    target_env: str,
) -> dict:
    logger.info("Getting all custom objects records difference")

    source_objects = CustomFieldsUtil.read_custom_fields_definition()
    target_objects = extract_custom_fields(environment=target_env)

    diff = CustomFieldsUtil.diff(
        source_objects=source_objects,
        target_objects=target_objects,
    )

    if not diff:
        return None

    output_dir = ZUORA_VCS_DIR.joinpath("temp/custom_fields")
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir.joinpath("diff.json")

    logger.info("Writing custom fields diff into file...")
    logger.info(f"🟢  {output_file.as_posix()}")
    with open(output_file, "w") as fs:
        json.dump(diff, fs, indent=4)

    return diff
