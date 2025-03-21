from typing import Dict, List
from packaging.version import Version

from common.lib.logger import logger
from common.app.zuora.api import ZuoraAPI
from common.app.zuora.validator import validate_environment


class ZuoraWorkflowUtil:
    @staticmethod
    def get_workflow_version_map_by_workflow_name(
        environment: str,
        workflow_name: str,
    ) -> dict:
        logger.info(f"Listing workflow {workflow_name} versions")
        logger.info(f"Zuora environment: {environment}")
        validate_environment(environment)

        url = f"workflows?name={workflow_name}"

        zuora_api = ZuoraAPI(environment)

        response = zuora_api.get(path=url)
        version_map = {}

        if response.status_code == 200:
            response_json = response.json()
            logger.info(response.json()["pagination"])
            data = response_json["data"][0]
            active_version = data["active_version"]
            logger.info(
                f"{active_version['version']} - {active_version['definitionId']}"
            )
            version_map[active_version["version"]] = {
                "definition_id": active_version["definitionId"],
                "description": active_version["description"],
            }

            latest_inactive_versions = data["latest_inactive_versions"]
            for inactive_version in latest_inactive_versions:
                logger.info(
                    f"{inactive_version['version']} - {inactive_version['definitionId']}"
                )

                version_map[inactive_version["version"]] = {
                    "definition_id": inactive_version["definitionId"],
                    "description": inactive_version["description"],
                }
        else:
            logger.info(f"No successful response: {response.json()}")

        return version_map

    @staticmethod
    def get_workflow_id(version_map: Dict[str, int]) -> int:
        for key, value in version_map.items():
            return value["definition_id"]

    @staticmethod
    def filter_task_by_id(task_id: str, tasks: List[dict]) -> dict:
        for task in tasks:
            if task["id"] == task_id:
                logger.info(f"Task found with ID: {task_id}")
                return task
        return {}

    @staticmethod
    def export_workflow_definition(
        environment: str,
        workflow_id: int,
        workflow_version: str,
    ):
        logger.info(
            f"Exporting workflow {workflow_id} details for version {workflow_version}"
        )
        logger.info(f"Zuora environment: {environment}")
        validate_environment(environment)

        url = f"workflows/{workflow_id}/export?version={workflow_version}"

        zuora_api = ZuoraAPI(environment)

        response = zuora_api.get(url)

        if response.status_code == 200:
            response_json = response.json()
            wf_metadata = response_json["workflow"]
            wf_def_metadata = response_json["workflow_definition"]

            wf_tasks = response_json["tasks"]
            wf_linkages = response_json["linkages"]

            linkages = []
            for linkage in wf_linkages:
                source_task_id = linkage["source_task_id"]
                target_task_id = linkage["target_task_id"]
                linkage_type = linkage["linkage_type"]
                source_workflow_id = linkage["source_workflow_id"]

                source_task = ZuoraWorkflowUtil.filter_task_by_id(
                    source_task_id, wf_tasks
                )
                target_task = ZuoraWorkflowUtil.filter_task_by_id(
                    target_task_id, wf_tasks
                )
                source_task_name = source_task.get("name", source_task_id)
                target_task_name = target_task.get("name", target_task_id)

                linkages.append(
                    {
                        "source_workflow_id": source_workflow_id,
                        "source_task_name": source_task_name,
                        "target_task_name": target_task_name,
                        "linkage_type": linkage_type,
                    }
                )

            sorted_linkages = sorted(
                linkages, key=lambda x: str(x["source_task_name"]), reverse=True
            )
            return {
                "workflow": wf_metadata,
                "workflow_definition": wf_def_metadata,
                "tasks": wf_tasks,
                "linkages": sorted_linkages,
            }
        else:
            logger.info(f"❌ No successful response: {response.json()}")

    @staticmethod
    def get_new_version_tag(version_map: Dict[str, int]) -> str:
        versions = list(version_map.keys())
        sorted_versions = sorted(versions, key=lambda version: Version(version))
        logger.info(f"unsorted_versions == {versions}")
        logger.info(f"sorted_versions == {sorted_versions}")
        max_version = sorted_versions[-1]
        max_version_items = max_version.split(".")
        minor_release = int(max_version_items[-1])
        new_version = ".".join(max_version_items[:-1]) + f".{minor_release + 1}"
        return new_version

    @staticmethod
    def get_target_workflow_id_and_version(environment: str, workflow_name: str):
        version_map = ZuoraWorkflowUtil.get_workflow_version_map_by_workflow_name(
            environment=environment,
            workflow_name=workflow_name,
        )

        workflow_id = ZuoraWorkflowUtil.get_workflow_id(version_map)
        new_version = ZuoraWorkflowUtil.get_new_version_tag(version_map)
        return workflow_id, new_version
