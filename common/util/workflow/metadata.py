import json
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR


class WorkflowMetadataUtil:
    @staticmethod
    def dump_workflow_metadata(
        workflow_metadata: dict,
        workflow_def_metadata: dict,
        dirname: str,
    ):
        logger.info("Exporting workflow metadata to file")
        workflow = {
            "workflow_definition": workflow_def_metadata,
            "workflow": workflow_metadata,
        }
        workflows_dir = ZUORA_VCS_DIR.joinpath("workflows")
        output_file = workflows_dir.joinpath(f"{dirname}/workflow.json")
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, "w") as fs:
            json.dump(workflow, fs, indent=4)
