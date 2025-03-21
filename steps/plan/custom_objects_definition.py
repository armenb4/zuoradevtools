import json
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from steps.extract.custom_objects_definition import extract_custom_objects_definitions
from common.util.custom_objects_definitions import CustomObjectsDefinitionUtil


def get_custom_objects_definitions_diff(
    target_env: str,
) -> dict:
    logger.info("Getting all custom objects records difference")

    source_definitions = CustomObjectsDefinitionUtil.read_custom_objects_definition()
    target_definitions = extract_custom_objects_definitions(environment=target_env)

    diff = CustomObjectsDefinitionUtil.diff(
        source_definitions=source_definitions,
        target_definitions=target_definitions,
    )

    if not diff:
        return None

    output_dir = ZUORA_VCS_DIR.joinpath("temp/custom_objects")
    output_dir.mkdir(exist_ok=True, parents=True)
    output_file = output_dir.joinpath("diff.json")

    logger.info("Writing custom objects definition diff into file...")
    logger.info(f"🟢  {output_file.as_posix()}")
    with open(output_file, "w") as fs:
        json.dump(diff, fs, indent=4)

    return diff
