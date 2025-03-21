import json
from typing import List
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.app.zuora.api import ZuoraAPI
from common.util.workflow.util import ZuoraWorkflowUtil


VALID_ENVIRONMENTS = ("dev", "qa", "uat", "prod")


def deploy_all_workflows(environment: str, workflow_names: List[str]):
    logger.info(f"Deploying all workflows to Zuora {environment.upper()}")
    for workflow_name in workflow_names:
        deploy_workflow(
            environment=environment,
            workflow_name=workflow_name,
        )
    logger.info("✅ Successfully deployed all workflows")


def deploy_workflow(environment: str, workflow_name: str):
    logger.info(f"Deploying workflow to Zuora {environment.upper()}")
    logger.info(f"Workflow: {workflow_name}")
    workflow_deploy_content_file = ZUORA_VCS_DIR.joinpath(
        "temp", "workflows", f"{workflow_name}-output-to-zuora.json"
    )
    if not workflow_deploy_content_file.exists():
        logger.info(
            f"❌ Cannot deploy {workflow_name} since {workflow_deploy_content_file} does not exist."
        )
        return

    zuora_api = ZuoraAPI(environment)

    # Get workflow id and new version tag on target environment by workflow name
    workflow_id, new_version = ZuoraWorkflowUtil.get_target_workflow_id_and_version(
        environment=environment,
        workflow_name=workflow_name,
    )

    url = f"workflows/{workflow_id}/versions/import?version={new_version}"

    # TODO: when it is a new workflow, we will not be able to get workflow_id in target environment...
    #  need to create option to publish as new workflow...

    with open(workflow_deploy_content_file) as fs:
        workflow_content = json.load(fs)

    payload = json.dumps(workflow_content)

    response = zuora_api.post(path=url, payload=payload)
    if response.status_code == 200:
        logger.info(f"✅ Successfully deployed {workflow_name} v{new_version}")
    else:
        logger.error(f"❌ Failed to deploy {workflow_name} v{new_version}")
        logger.error(response.text)
