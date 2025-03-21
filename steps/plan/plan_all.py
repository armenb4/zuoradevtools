import shutil
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from steps.plan.custom_fields import get_custom_fields_diff
from steps.plan.workflow import generate_all_workflow_jsons
from steps.plan.custom_object_records import get_custom_objects_records_diff
from steps.plan.billing_doc import generate_all_html_template_payloads
from steps.plan.custom_objects_definition import get_custom_objects_definitions_diff


def plan_all(request_form: dict):
    """
    Given deployment parameters in ``input-plan-deploy.json``. \n
    Prepares deployment ready JSONs for: \n
    - Workflows \n
    - Configuration templates \n
    - Custom object records  \n
    """
    logger.info("🟣 Running planning step")
    logger.info(f"Request form: {request_form}")

    target_env = request_form["target_env"]

    plan_output_dir = ZUORA_VCS_DIR.joinpath("temp")

    try:
        logger.info("Trying to clean up PLAN directory")
        logger.info(plan_output_dir.as_posix())
        shutil.rmtree(plan_output_dir)
    except Exception:
        pass
    plan_output_dir.mkdir(exist_ok=True, parents=True)

    # Custom fields for standard objects
    include_custom_fields = request_form.get("include_custom_fields", False)
    if include_custom_fields:
        try:
            logger.info("🟡 Generating custom fields JSONs")
            get_custom_fields_diff(target_env)
            logger.info("✅ Successfully generated all custom fields JSONs")
        except Exception as e:
            logger.info("❌ FAILED to generate all custom fields JSONs")
            logger.info(e)
    else:
        logger.info("Skipping custom fields generation")

    # Custom object definitions
    include_custom_object_definitions = request_form.get(
        "include_custom_object_definitions", False
    )
    if include_custom_object_definitions:
        try:
            logger.info("🟡 Generating custom object definitions")
            get_custom_objects_definitions_diff(target_env)
            logger.info("✅ Successfully generated all custom object definitions")
        except Exception as e:
            logger.info("❌ FAILED to generate all custom object definitions")
            logger.info(e)
    else:
        logger.info("Skipping custom object definitions generation")

    # Custom object records
    include_custom_object_records = request_form.get(
        "include_custom_object_records", False
    )
    if include_custom_object_records:
        try:
            logger.info("🟡 Getting custom object records difference")
            get_custom_objects_records_diff(target_env)
            logger.info("✅ Successfully got all custom object records difference")
        except Exception as e:
            logger.info("❌ FAILED to get custom object records difference")
            raise e
    else:
        logger.info("Skipping custom object records difference generation")

    # Billing document templates (Out of the box HTML templates)
    include_html_templates = request_form.get("include_html_templates", False)
    if include_html_templates:
        try:
            logger.info("🟡 Generating all HTML template Payloads")
            generate_all_html_template_payloads(environment=target_env)
            logger.info("✅ Successfully generated all HTML template Payloads")
        except Exception as e:
            logger.info("❌ FAILED to generate all HTML template Payloads")
            logger.info(e)
    else:
        logger.info("Skipping HTML template Payloads generation")

    # Workflows
    workflow_names = request_form.get("workflows", [])
    if workflow_names:
        try:
            logger.info("🟡 Generating workflow JSONs")
            generate_all_workflow_jsons(
                environment=target_env,
                workflow_names=workflow_names,
            )
            logger.info("✅ Successfully generated all workflow JSONs")
        except Exception as e:
            logger.info("❌ FAILED to generate all workflow JSONs")
            logger.info(e)
    else:
        logger.info("Skipping workflow generation")

    logger.info("🟢🟢🟢 Planning step completed 🟢🟢🟢")
    return "success"
