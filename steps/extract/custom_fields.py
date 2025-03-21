from common.lib.logger import logger
from common.app.zuora.api import ZuoraAPI
from common.util.custom_fields.util import CustomFieldsUtil, ZUORA_OBJECTS


def extract_custom_fields(environment: str) -> dict:
    logger.info(
        f"🟡 Extracting custom object records from Zuora environment {environment.upper()}"
    )

    zuora_api = ZuoraAPI(environment)

    all_custom_fields = {}
    for object_name in ZUORA_OBJECTS:
        definition_url = f"objects/definitions/com_zuora/{object_name}"
        logger.info(f"Get request to {definition_url}")
        response = zuora_api.get(definition_url)
        response_json = response.json()

        if response.status_code != 200:
            raise Exception(f"Unable to retrieve object definition. {response.text}")

        schema: dict = response_json.get("schema", {})
        properties: dict[str, dict] = response_json["schema"]["properties"]
        custom_fields = {
            field_name: field_definition
            for field_name, field_definition in properties.items()
            if field_definition.get("origin") == "custom"
        }

        all_custom_fields[object_name] = {
            "custom_fields": custom_fields,
            "read_only": schema.get("readonlyOnUI", []),
            "filterable": schema.get("filterable", []),
        }

    return all_custom_fields


def extract_custom_fields_to_file(environment: str):
    custom_fields = extract_custom_fields(environment=environment)

    for object_name, object_fields in custom_fields.items():
        CustomFieldsUtil.dump_custom_fields_definition(object_fields, object_name)
