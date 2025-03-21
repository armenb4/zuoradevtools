from common.lib.logger import logger
from steps.deploy.workflow import deploy_all_workflows
from steps.deploy.billing_doc import deploy_all_billing_document_templates
from steps.deploy.custom_objects_records import deploy_all_custom_object_records_diff
from steps.deploy.custom_fields import deploy_all_custom_fields_diff
from steps.deploy.custom_objects_definition import (
    deploy_all_custom_object_definitions_diff,
)


def deploy_all(request_form: dict):
    """
    Given deployment parameters in ``input-plan-deploy.json``. \n
    Uses deployment ready JSONs that were prepared by plan to: \n
    - Deploy Workflows \n
    - Deploy Billing Document templates \n
    - Deploy Custom object definitions  \n
    - Deploy Custom object records      \n
    - Deploy Custom fields              \n
    """
    logger.info("🟣 Running deployment step")
    logger.info(f"Request form: {request_form}")

    target_env: str = request_form["target_env"]

    logger.info(f"Target environment is: {target_env.upper()}")

    # Custom fields for standard objects
    include_custom_fields = request_form.get("include_custom_fields", False)
    if include_custom_fields:
        deploy_all_custom_fields_diff(target_env)
    else:
        logger.info("Skipping Custom Fields deployment")

    # Custom object definitions
    include_custom_object_definitions = request_form.get(
        "include_custom_object_definitions", False
    )
    if include_custom_object_definitions:
        deploy_all_custom_object_definitions_diff(target_env)
    else:
        logger.info("Skipping Custom Object Definitions deployment")

    # Custom object records
    include_custom_object_records = request_form.get(
        "include_custom_object_records", False
    )
    if include_custom_object_records:
        deploy_all_custom_object_records_diff(target_env)
    else:
        logger.info("Skipping Custom Object Records deployment")

    # Billing document templates (Out of the box HTML templates)
    include_html_templates = request_form.get("include_html_templates", False)
    if include_html_templates:
        deploy_all_billing_document_templates(environment=target_env)
    else:
        logger.info("Skipping Billing Document Templates deployment")

    # Workflows
    workflow_names = request_form.get("workflows", [])
    if workflow_names:
        deploy_all_workflows(
            environment=target_env,
            workflow_names=workflow_names,
        )
    else:
        logger.info("Skipping Workflows deployment")

    logger.info("🟢🟢🟢 Deployment step completed 🟢🟢🟢")
