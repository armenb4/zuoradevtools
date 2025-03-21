from common.config import config
from common.lib.logger import logger
from tkinter import Tk, ttk, BooleanVar, StringVar
from common.util.workflow.util import ZuoraWorkflowUtil
from steps.extract.extract_all import extract_all
from gui.checkbox_options import CHECKBOX_OPTIONS
from gui.style import get_style


class Application(ttk.Frame):
    def __init__(self, main_window: Tk):
        super().__init__(main_window)
        main_window.title("Zuora Deployment Automation Tool - Extract")

        label = ttk.Label(self, text="Select items to extract")
        label.place(x=400, y=10)

        # Pick Zuora environment for data extraction
        environment_label = ttk.Label(self, text="Source environment")
        environment_label.place(x=20, y=35)
        self.environment_chosen = StringVar()
        self.environment_chosen.trace_add("write", self.fetch_workflow_versions)
        self.environment_box = ttk.Combobox(
            self,
            values=["dev", "qa", "uat"],
            state="readonly",
            textvariable=self.environment_chosen,
        )
        self.environment_box.place(x=150, y=30)

        self.checkboxes: list[ttk.Checkbutton] = []
        self.checkboxes_values: list[tuple[str, BooleanVar]] = []

        self.style = get_style()

        self.checkbox_counter = 0
        for key, value in CHECKBOX_OPTIONS.items():
            is_disabled = value["disabled"]
            if is_disabled:
                continue

            checkbox_value = BooleanVar(self)
            checkbox_value.set(value["default"])
            self.checkboxes_values.append((key, checkbox_value))

            checkbox = ttk.Checkbutton(
                self,
                text=value["name"],
                variable=checkbox_value,
            )

            checkbox.place(x=20, y=60 + 35 * self.checkbox_counter)
            self.checkboxes.append(checkbox)
            self.checkbox_counter += 1

        workflows_label = ttk.Label(self, text="Select Workflows to extract")
        workflows_label.place(x=20, y=250)

        # Set default environment and fetch workflow versions
        self.workflow_checkboxes: list[ttk.Checkbutton] = []
        self.workflow_checkboxes_values: list[tuple[str, BooleanVar]] = []
        self.workflow_versions: list[ttk.Combobox] = []
        self.environment_box.set("dev")

        button = ttk.Button(
            text="EXTRACT",
            command=self.extract_selected,
            style="TButton",
        )
        button.place(x=400, y=300 + 35 * self.checkbox_counter)

        self.place(width=800, height=400 + 35 * self.checkbox_counter)
        main_window.minsize(1000, 400 + 35 * self.checkbox_counter)

    def fetch_workflow_versions(self, *args, **kwargs):
        # Reset workflow checkboxes
        if self.workflow_checkboxes:
            for checkbox in self.workflow_checkboxes:
                try:
                    checkbox.destroy()
                except Exception:
                    pass

        # Reset workflow version checkboxes
        if self.workflow_versions:
            for version_box in self.workflow_versions:
                try:
                    version_box.destroy()
                except Exception:
                    pass

        self.workflow_checkboxes: list[ttk.Checkbutton] = []
        self.workflow_versions: list[ttk.Combobox] = []
        self.workflow_checkboxes_values: list[tuple[str, BooleanVar]] = []

        self.fetch_data_from_zuora(self.environment_box.get())

        checkbox_counter = 0
        for workflow in self.workflows:
            workflow_value = BooleanVar(self)
            workflow_value.set(workflow["default"])
            self.workflow_checkboxes_values.append((workflow["name"], workflow_value))

            workflow_checkbox = ttk.Checkbutton(
                self,
                text=workflow["name"],
                variable=workflow_value,
                command=self.workflow_checkbox_clicked,
            )
            workflow_checkbox.place(x=20, y=280 + 35 * checkbox_counter)
            self.workflow_checkboxes.append(workflow_checkbox)

            version_box = ttk.Combobox(
                self,
                state="disabled",
                values=[
                    f"{version['number']} - {version['description']}"
                    for version in workflow["versions"]
                ],
            )
            version_box.configure(width=100)
            version_box.place(x=300, y=280 + 35 * checkbox_counter)
            self.workflow_versions.append(version_box)

            checkbox_counter += 1

        self.checkbox_counter += checkbox_counter

    def fetch_data_from_zuora(self, environment: str = "dev"):
        self.workflows = []

        for workflow_name in config.WORKFLOW_NAMES:
            try:
                workflow_version_map = (
                    ZuoraWorkflowUtil.get_workflow_version_map_by_workflow_name(
                        workflow_name=workflow_name,
                        environment=environment,
                    )
                )
            except Exception:
                continue

            workflow = {
                "name": workflow_name,
                "default": False,
                "versions": [
                    {"number": version_key, "description": details["description"]}
                    for version_key, details in workflow_version_map.items()
                ],
            }
            self.workflows.append(workflow)

    def workflow_checkbox_clicked(self, *args, **kwargs):
        for index, checkbox in enumerate(self.workflow_checkboxes):
            if self.workflow_checkboxes_values[index][1].get():
                self.workflow_versions[index].config(state="readonly")
            else:
                self.workflow_versions[index].config(state="disabled")
                self.workflow_versions[index].set("")

    def extract_selected(self):
        logger.info("Extracting selected items")

        request_form = {"source_environment": self.environment_box.get()}

        logger.info("🟢 Checkboxes")
        for index, checkbox in enumerate(self.checkboxes):
            is_selected = self.checkboxes_values[index][1].get()
            if not is_selected:
                continue

            logger.info(f"Checkbox {checkbox.cget('text')} is selected")
            request_form[self.checkboxes_values[index][0]] = is_selected

        request_form["workflows"] = []
        logger.info("🟢 Workflow Checkboxes")
        for index, workflow_checkbox in enumerate(self.workflow_checkboxes):
            is_selected = self.workflow_checkboxes_values[index][1].get()
            if not is_selected:
                continue

            selected_version = self.workflow_versions[index].get().split(" - ")[0]
            if not selected_version:
                continue
            logger.info(f"Workflow {workflow_checkbox.cget('text')} is selected")
            logger.info(f"Version {selected_version} is selected")
            request_form["workflows"].append(
                {
                    "name": workflow_checkbox.cget("text"),
                    "version": selected_version,
                }
            )

        extract_all(request_form)


def run_app_for_extract():
    main_window = Tk()
    app = Application(main_window)
    app.mainloop()
