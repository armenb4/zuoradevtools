from common.lib.logger import logger
from common.app.zuora.api import ZuoraAPI
from common.util.custom_objects_definitions import CustomObjectsDefinitionUtil
from common.config.config import CUSTOM_OBJECT_NAMES

KEYS_TO_REMOVE = [
    "Id",
    "type",
    "CreatedById",
    "UpdatedById",
    "CreatedDate",
    "UpdatedDate",
]


def extract_custom_objects_definitions(
    environment: str,
) -> dict:
    logger.info(
        f"🟡 Extracting custom object definitions from Zuora environment {environment.upper()}"
    )

    zuora_api = ZuoraAPI(environment)

    custom_objects = {}
    for custom_object_name in CUSTOM_OBJECT_NAMES:
        definition_url = f"objects/definitions/default/{custom_object_name}"
        logger.info(f"Get request to {definition_url}")
        response = zuora_api.get(definition_url)
        if response.status_code == 200:
            response_json = response.json()
            CustomObjectsDefinitionUtil.remove_keys_from_dict(
                response_json, KEYS_TO_REMOVE
            )

            custom_objects[custom_object_name] = response_json
        else:
            logger.error(
                f"Failed to extract custom object definition for {custom_object_name}"
            )
            logger.error(response.text)

    return custom_objects


def extract_custom_objects_definitions_to_file(
    environment: str,
) -> dict:
    custom_object_definitions = extract_custom_objects_definitions(
        environment=environment,
    )

    for custom_object_name, definition in custom_object_definitions.items():
        CustomObjectsDefinitionUtil.dump_object_definition(
            definition, custom_object_name
        )

    return custom_object_definitions
