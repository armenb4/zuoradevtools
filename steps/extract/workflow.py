import shutil

from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.app.zuora.validator import validate_environment
from common.util.workflow.util import ZuoraWorkflowUtil
from common.util.workflow.task import WorkflowTaskUtil
from common.util.workflow.linkage import WorkflowLinkageUtil
from common.util.workflow.metadata import WorkflowMetadataUtil


VALID_ENVIRONMENTS = ("dev", "qa", "uat", "prod")


def extract_workflow_src_code(
    environment: str,
    workflow_name: str,
    workflow_version: str,
    temp: bool = False,
):
    logger.info("Input validation")
    validate_environment(environment)

    logger.info(f"Zuora environment: {environment}")
    logger.info(f"Workflow name:     {workflow_name}")
    logger.info(f"Workflow version:  {workflow_version}")
    logger.info(f"Temp mode:         {temp}")

    version_map = ZuoraWorkflowUtil.get_workflow_version_map_by_workflow_name(
        environment=environment,
        workflow_name=workflow_name,
    )
    workflow_id = version_map.get(workflow_version)["definition_id"]
    logger.info(f"Workflow id is {workflow_id}")
    if workflow_id:
        workflow_definition = ZuoraWorkflowUtil.export_workflow_definition(
            environment=environment,
            workflow_id=workflow_id,
            workflow_version=workflow_version,
        )

        if temp:
            output_dirname = f".temp/{environment}/{workflow_name}/{workflow_version}"
        else:
            output_dirname = workflow_name

        if workflow_definition:
            logger.info("Dumping workflow definition")

            try:
                output_dir = ZUORA_VCS_DIR.joinpath("workflows", output_dirname)
                logger.info(f"Trying to cleanup workflow directory {output_dir} ")
                shutil.rmtree(output_dir)
            except Exception as e:
                logger.info(e)
                pass
            wf_metadata = workflow_definition.get("workflow")
            wf_def_metadata = workflow_definition.get("workflow_definition")

            wf_metadata["id"] = 1
            WorkflowMetadataUtil.dump_workflow_metadata(
                wf_metadata, wf_def_metadata, output_dirname
            )

            tasks = workflow_definition.get("tasks")
            linkages = workflow_definition.get("linkages")
            WorkflowTaskUtil.dump_tasks(tasks, output_dirname)
            WorkflowLinkageUtil.dump_linkages(linkages, output_dirname)
