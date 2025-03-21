import json
from typing import List
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR


class WorkflowLinkageUtil:
    @staticmethod
    def create_linkages_with_id(
        linkages_src: List[dict], task_map_src: dict
    ) -> List[dict]:
        linkages_dest: List[dict] = []

        for linkage in linkages_src:
            source_task_id: int = task_map_src.get(linkage["source_task_name"])
            target_task_id: int = task_map_src.get(linkage["target_task_name"])

            linkages_dest.append(
                {
                    "source_workflow_id": linkage["source_workflow_id"],
                    "source_task_id": source_task_id,
                    "target_task_id": target_task_id,
                    "linkage_type": linkage["linkage_type"],
                }
            )

        return linkages_dest

    @staticmethod
    def dump_linkages(linkages: List[dict], dirname: str):
        logger.info("Exporting workflow linkages information to file")
        workflows_dir = ZUORA_VCS_DIR.joinpath("workflows")
        output_file = workflows_dir.joinpath(f"{dirname}/linkages.json")
        output_file.parent.mkdir(exist_ok=True, parents=True)

        for link in linkages:
            if link["linkage_type"] == "Start":
                link["source_workflow_id"] = 1
            else:
                link["source_workflow_id"] = None

        with open(output_file, "w") as fs:
            json.dump(linkages, fs, indent=4)
