import json
from pathlib import Path
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.util.workflow.task import WorkflowTaskUtil
from common.util.workflow.linkage import WorkflowLinkageUtil


def generate_workflow_json(workflow_name: str, output_dir: Path):
    logger.info("Generating workflow JSON")
    logger.info(f"Workflow name:    {workflow_name}")

    workflows_dir = ZUORA_VCS_DIR.joinpath("workflows")
    source_code_dir = workflows_dir.joinpath(workflow_name).resolve()

    linkage_file = source_code_dir.joinpath("linkages.json")
    with open(linkage_file) as fs:
        linkages_src = json.load(fs)

    task_map_file = source_code_dir.joinpath("task_map.json")
    with open(task_map_file) as fs:
        task_map_src = json.load(fs)

    workflow_metadata_file = source_code_dir.joinpath("workflow.json")
    with open(workflow_metadata_file) as fs:
        workflow = json.load(fs)

    linkages_dest = WorkflowLinkageUtil.create_linkages_with_id(
        linkages_src, task_map_src
    )

    task_files = list(source_code_dir.joinpath("tasks").glob("*"))
    tasks_dest = WorkflowTaskUtil.create_task_definitions(task_map_src, task_files)

    workflow["tasks"] = tasks_dest
    workflow["linkages"] = linkages_dest

    output_file = output_dir.joinpath(f"{workflow_name}-output-to-zuora.json")
    output_dir.mkdir(exist_ok=True, parents=True)
    with open(output_file, "w") as fs:
        json.dump(workflow, fs, indent=4)


def generate_all_workflow_jsons(environment: str, workflow_names: str):
    logger.info(
        f"Generating all workflow JSONs to upload to Zuora {environment.upper()}"
    )
    output_dir = ZUORA_VCS_DIR.joinpath("temp/workflows")

    for workflow_name in workflow_names:
        try:
            logger.info(f"Generating workflow JSON for {workflow_name}")
            generate_workflow_json(workflow_name, output_dir)
            logger.info(f"✅ Successfully generated workflow JSON for {workflow_name}")
        except Exception as e:
            logger.error(f"❌ FAILED to generate workflow JSON for {workflow_name}")
            logger.error(f"❌ {e}")
