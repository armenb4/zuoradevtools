from pathlib import Path
from common.config import config
from common.lib.logger import logger
from steps.extract.workflow import extract_workflow_src_code
from steps.extract.billing_doc import export_all_billing_document_templates
from steps.extract.custom_fields import extract_custom_fields
from steps.extract.custom_objects_definition import extract_custom_objects_definitions
from steps.extract.custom_object_records import extract_custom_object_records_to_file

root_dir = Path(__file__).parent.parent.parent


def extract_all(request_form: dict):
    logger.info("🟣 Running extraction step")
    logger.info(f"Request form: {request_form}")

    source_environment = request_form["source_environment"]

    # Custom fields for standard objects
    include_custom_fields = request_form.get("include_custom_fields", False)
    if include_custom_fields:
        try:
            logger.info("Extracting custom fields")
            extract_custom_fields(environment=source_environment)
        except Exception as e:
            logger.info("❌ FAILED to extract custom fields")
            raise e
    else:
        logger.info("Skipping custom fields extraction")

    # Custom objects definition
    include_custom_object_definitions = request_form.get(
        "include_custom_object_definitions", False
    )
    if include_custom_object_definitions:
        logger.info("Extracting custom object definitions")
        try:
            extract_custom_objects_definitions(environment=source_environment)
            logger.info("✅ Successfully extracted custom object definitions")
        except Exception as e:
            logger.info("❌ FAILED to extract custom object definitions")
            logger.info(e)
    else:
        logger.info("Skipping custom object definitions extraction")

    # Custom object records
    include_custom_object_records = request_form.get(
        "include_custom_object_records", False
    )
    if include_custom_object_records:
        try:
            logger.info("Extracting custom object records")
            extract_custom_object_records_to_file(
                environment=source_environment,
                custom_object_names=config.CUSTOM_OBJECT_NAMES,
                remove_keys=True,
            )
            logger.info("✅ Successfully extracted custom object records")
        except Exception as e:
            logger.info("❌ FAILED to extract custom object records")
            logger.info(e)
    else:
        logger.info("Skipping custom object records extraction")

    # Billing document templates (Out of the box HTML templates)
    include_html_templates = request_form.get("include_html_templates", False)
    if include_html_templates:
        try:
            logger.info("Extracting billing document templates")
            export_all_billing_document_templates(environment=source_environment)
        except Exception as e:
            logger.info("❌ FAILED to extract all billing document templates")
            raise e
    else:
        logger.info("Skipping billing document templates extraction")

    # Workflows
    workflows = request_form.get("workflows", [])
    if workflows:
        for workflow in workflows:
            try:
                logger.info(
                    f"Extracting workflow source code for {workflow['name']} and {workflow['version']}"
                )
                extract_workflow_src_code(
                    environment=source_environment,
                    workflow_name=workflow["name"],
                    workflow_version=workflow["version"],
                )
                logger.info(
                    f"✅ Successfully extracted workflow source code for {workflow['name']}"
                )
            except Exception as e:
                logger.info(
                    f"❌ FAILED to extract workflow source code for {workflow['name']}"
                )
                raise e
    else:
        logger.info("Skipping workflow source code extraction")

    logger.info("🟢🟢🟢 Extracting step completed 🟢🟢🟢")
