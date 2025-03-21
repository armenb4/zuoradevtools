import json
from typing import List
from pathlib import Path
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR


class NotValidZuoraWorkflowTaskName(Exception):
    pass


class WorkflowTaskUtil:
    @staticmethod
    def find_task_file(task_filename: str, task_files: List[Path]) -> Path:
        for file in task_files:
            if task_filename == file.name:
                return file
        return None

    @staticmethod
    def create_task_definitions(
        task_map_src: dict,
        task_files: List[Path],
    ) -> List[dict]:
        tasks_dest: List[dict] = []

        for task_name, task_id in task_map_src.items():
            logger.info(f"Building task data {task_name}")

            task_definition_file = WorkflowTaskUtil.find_task_file(
                f"{task_name}.json", task_files
            )
            if not task_definition_file:
                logger.info(f"🚩🚩🚩Task definition file not found: {task_name}")
                continue

            with open(task_definition_file) as fs:
                task_definition: dict = json.load(fs)

            task_action_type = task_definition["action_type"]

            if task_action_type == "If":
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.liquid", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["if_clause"] = src_code

            elif task_action_type == "Logic::Liquid":
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.liquid", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["code"] = src_code

            elif task_action_type == "Logic::Case":
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.liquid", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["case_clause"] = src_code

            elif task_action_type == "Script::JavaScript":
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.js", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["code"] = src_code

            elif task_action_type in ("Logic::JSONTransform"):
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.jsonata", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["template"] = src_code

            elif task_action_type in ("Data::Link"):
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.sql", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["query"] = src_code

            elif task_action_type in ("Email"):
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.html", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["email"]["template"] = src_code

            elif task_action_type in (
                "File::CustomPDF::CustomDocument",
                "Billing::CustomBillingDocument",
            ):
                code_file = WorkflowTaskUtil.find_task_file(
                    f"{task_name}.html", task_files
                )
                if code_file:
                    src_code = code_file.read_text()
                    task_definition["parameters"]["template"] = src_code

            task_definition["id"] = task_id
            task_definition["name"] = task_name
            tasks_dest.append(task_definition)

        return tasks_dest

    @staticmethod
    def get_task_name_by_id(task_map: dict, id: int) -> str:
        for task_name, task_id in task_map.items():
            if int(task_id) == int(id):
                return task_name
        return None

    @staticmethod
    def get_id_from_filename(filename: str) -> int:
        suffix = filename.split("__")[-1]
        id = suffix.split(".")[0]

        try:
            return int(id)
        except Exception:
            return None

    @staticmethod
    def update_id_in_file(file: str, task_map_original: dict, task_map_new: dict):
        logger.info(f"Updating id in file or object: {file}")

        id_in_file = WorkflowTaskUtil.get_id_from_filename(file)
        if not id_in_file:
            logger.info(f"ID in file {id_in_file}")
            return file

        task_name = WorkflowTaskUtil.get_task_name_by_id(task_map_original, id_in_file)
        if not task_name:
            logger.info(f"🚩New id not found to replace id {id_in_file}")
            return file

        new_id = task_map_new[task_name]

        logger.info(f"🆕 ID replacement: {id_in_file} by {new_id}")
        updated_file = file.replace(str(id_in_file), str(new_id))
        logger.info(f"🆕 New file or object: {updated_file}")
        return updated_file

    @staticmethod
    def update_ids_in_files_for_callout_task(
        files: List[dict], task_map_original: dict, task_map_new: dict
    ):
        for file_obj in files:
            file = file_obj["key"]
            updated_file = WorkflowTaskUtil.update_id_in_file(
                file=file,
                task_map_original=task_map_original,
                task_map_new=task_map_new,
            )
            file_obj["key"] = updated_file
        return files

    @staticmethod
    def update_ids_in_files_for_email_task(
        files: dict, task_map_original: dict, task_map_new: dict
    ):
        updated_files = {}
        for filename, file_obj in files.items():
            updated_file = WorkflowTaskUtil.update_id_in_file(
                file=filename,
                task_map_original=task_map_original,
                task_map_new=task_map_new,
            )
            updated_files[updated_file] = file_obj
        return updated_files

    @staticmethod
    def dump_task_map_to_file(task_map: dict, filename: str):
        workflows_dir = ZUORA_VCS_DIR.joinpath("workflows")
        output_file = workflows_dir.joinpath(filename)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        with open(output_file, "w") as fs:
            json.dump(task_map, fs, indent=4)

    @staticmethod
    def dump_task_to_file(
        task: dict,
        file_basename: str,
        task_map_original: dict,
        task_map_new: dict,
    ):
        workflows_dir = ZUORA_VCS_DIR.joinpath("workflows")
        output_file = workflows_dir.joinpath(file_basename)
        output_file.parent.mkdir(exist_ok=True, parents=True)

        WorkflowTaskUtil.validate_filename(Path(file_basename).name)

        task_action_type: str = task["action_type"]
        task_parameters: dict = task["parameters"]
        task_name: str = task["name"]
        if "workflow_tags" in task_parameters:
            task_parameters.pop("workflow_tags")

        if "delete_payload_paths" in task_parameters:
            task_parameters.pop("delete_payload_paths")

        export_data_json = None
        export_data_sql = None
        export_data_js = None
        export_data_jsonata = None
        export_data_html = None
        export_data_liquid = None

        logger.info(f"Dumping task {task_name} to file")

        if task_action_type == "If":
            export_data_liquid: str = task_parameters.pop("if_clause")
            export_data_liquid = export_data_liquid.replace("\r", "")

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )
        elif task_action_type == "Logic::Liquid":
            export_data_liquid: str = task_parameters.pop("code")
            export_data_liquid = export_data_liquid.replace("\r", "")

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )
        elif task_action_type == "Logic::Case":
            export_data_liquid: str = task_parameters.pop("case_clause")
            export_data_liquid = export_data_liquid.replace("\r", "")

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )
        elif task_action_type == "Script::JavaScript":
            export_data_js: str = task_parameters.pop("code")
            export_data_js = export_data_js.replace("\r", "")

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )

        elif task_action_type in ("Logic::JSONTransform"):
            export_data_jsonata: str = task_parameters.pop("template")
            export_data_jsonata = export_data_jsonata.replace("\r", "")

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )

        elif task_action_type in ("Data::Link"):
            export_data_sql: str = task_parameters.pop("query")
            export_data_sql = export_data_sql.replace("\r", "")

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )

        elif task_action_type in ("Email"):
            email_def: dict = task_parameters["email"]
            export_data_html: str = email_def.pop("template")
            export_data_html = export_data_html.replace("\r", "")

            files = task_parameters.get("files")
            if files:
                updated_files = WorkflowTaskUtil.update_ids_in_files_for_email_task(
                    files=files,
                    task_map_original=task_map_original,
                    task_map_new=task_map_new,
                )
                task_parameters["files"] = updated_files

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )

        elif task_action_type in (
            "File::CustomPDF::CustomDocument",
            "Billing::CustomBillingDocument",
        ):
            export_data_html: str = task_parameters.pop("template")
            export_data_html = export_data_html.replace("\r", "")

            metadata = {
                "action_type": task_action_type,
                "parameters": task_parameters,
                "css": task["css"],
            }

            if "object_id" in task:
                metadata["object_id"] = task["object_id"]

            export_data_json = json.dumps(
                metadata,
                indent=4,
            )

        elif task_action_type in (
            "Update",
            "Execute::WorkflowTask",
            "CustomObject::Create",
        ):
            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                    "object": task["object"],
                    "object_id": task["object_id"],
                },
                indent=4,
            )

        elif task_action_type in (
            "Iterate",
            "Logic::CSVTranslator",
        ):
            task_object = task["object"]
            task_object = WorkflowTaskUtil.update_id_in_file(
                file=task_object,
                task_map_original=task_map_original,
                task_map_new=task_map_new,
            )

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                    "object": task_object,
                },
                indent=4,
            )

        elif task_action_type in (
            "Delay",
            "Callout",
            "GraphQuery",
            "File::DownloadFile",
        ):
            if "files" in task_parameters:
                files = task_parameters["files"]
                WorkflowTaskUtil.update_ids_in_files_for_callout_task(
                    files=files,
                    task_map_original=task_map_original,
                    task_map_new=task_map_new,
                )

            if "url" in task_parameters:
                url = task_parameters["url"]
                if "FileDownload" in url:
                    updated_url = WorkflowTaskUtil.update_id_in_file(
                        file=url,
                        task_map_original=task_map_original,
                        task_map_new=task_map_new,
                    )
                    task_parameters["url"] = updated_url

            export_data_json = json.dumps(
                {
                    "action_type": task_action_type,
                    "parameters": task_parameters,
                    "css": task["css"],
                },
                indent=4,
            )

        else:
            logger.info(
                f"🟡 🟡 🟡 🟡 Task action type has no specifics: {task_action_type}"
            )
            export_data_json = json.dumps(task, indent=4)

        # Export data to file
        if export_data_json:
            output_file = workflows_dir.joinpath(f"{file_basename}.json")
            output_file.write_text(export_data_json)

        if export_data_js:
            output_file = workflows_dir.joinpath(f"{file_basename}.js")
            output_file.write_text(export_data_js)

        if export_data_jsonata:
            output_file = workflows_dir.joinpath(f"{file_basename}.jsonata")
            output_file.write_text(export_data_jsonata, encoding="utf-8")

        if export_data_sql:
            output_file = workflows_dir.joinpath(f"{file_basename}.sql")
            output_file.write_text(export_data_sql, encoding="utf-8")

        if export_data_html:
            output_file = workflows_dir.joinpath(f"{file_basename}.html")
            output_file.write_text(export_data_html, encoding="utf-8")

        if export_data_liquid:
            output_file = workflows_dir.joinpath(f"{file_basename}.liquid")
            output_file.write_text(export_data_liquid, encoding="utf-8")

    @staticmethod
    def validate_duplicate_task_names(tasks: List[dict]) -> List[str]:
        task_names = []
        duplicate_tasks = []
        for task in tasks:
            task_name = task["name"]
            if task_name in task_names:
                logger.info(f"❌ duplicate task {task_name}")
                duplicate_tasks.append(task_name)
            else:
                task_names.append(task_name)

        return duplicate_tasks

    @staticmethod
    def get_task_map_original(tasks: List[dict]) -> dict:
        task_map = {}
        for task in tasks:
            task_map[task["name"]] = task["id"]

        return task_map

    def get_task_map_new_ids(tasks: List[dict]) -> dict:
        task_map = {}
        repeated_task_names = []

        for i, task in enumerate(tasks):
            if task["name"] in task_map:
                repeated_task_names.append(task["name"])

            task_map[task["name"]] = i + 1

        if repeated_task_names:
            logger.info("Repeated task names...")
            logger.info(repeated_task_names)
            logger.info("-------------------------------")

        return task_map

    @staticmethod
    def dump_tasks(tasks: List[dict], dirname: str):
        logger.info("Exporting workflow tasks to file")
        duplicate_tasks = WorkflowTaskUtil.validate_duplicate_task_names(tasks)
        duplicates_file = ZUORA_VCS_DIR.joinpath(f"workflows/{dirname}/duplicates.json")
        with open(duplicates_file, "w") as fs:
            json.dump(duplicate_tasks, fs)

        task_map_original = WorkflowTaskUtil.get_task_map_original(tasks)
        task_map_new = WorkflowTaskUtil.get_task_map_new_ids(tasks)
        WorkflowTaskUtil.dump_task_map_to_file(task_map_new, f"{dirname}/task_map.json")

        for task in tasks:
            task_name = task["name"]
            task_map_original[task_name] = task["id"]
            WorkflowTaskUtil.dump_task_to_file(
                task=task,
                file_basename=f"{dirname}/tasks/{task_name}",
                task_map_original=task_map_original,
                task_map_new=task_map_new,
            )

    @staticmethod
    def validate_filename(filename: str):
        # TODO: Replace by a regex
        if (
            "\\" in filename
            or "/" in filename
            or ":" in filename
            or "*" in filename
            or "?" in filename
            or '"' in filename
            or "<" in filename
            or ">" in filename
            or "|" in filename
        ):
            raise NotValidZuoraWorkflowTaskName(
                f"Task name includes non valid character: {filename}"
            )
