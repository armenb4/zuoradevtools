from common.config import config
from common.lib.logger import logger
from tkinter import Tk, ttk, BooleanVar
from steps.plan.plan_all import plan_all
from steps.deploy.deploy_all import deploy_all
from gui.checkbox_options import CHECKBOX_OPTIONS
from gui.style import get_style


class Application(ttk.Frame):
    def __init__(self, main_window: Tk):
        super().__init__(main_window)
        main_window.title("Zuora Deployment Automation Tool - plan and deploy")

        self.checkboxes: list[ttk.Checkbutton] = []
        self.checkboxes_values: list[tuple[str, BooleanVar]] = []
        checkbox_counter = 0
        label = ttk.Label(self, text="Select componets for planning and deployment")
        label.place(x=400, y=10)

        environment_label = ttk.Label(self, text="Target environment")
        environment_label.place(x=20, y=35)

        self.environment_box = ttk.Combobox(
            self,
            values=["dev", "qa", "uat"],
            state="readonly",
        )
        self.environment_box.place(x=150, y=30)
        self.environment_box.set("qa")

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
                command=self.any_state_change,
            )

            checkbox.place(x=20, y=60 + 35 * checkbox_counter)
            self.checkboxes.append(checkbox)
            checkbox_counter += 1

        workflows_label = ttk.Label(self, text="Workflows")
        workflows_label.place(x=20, y=250)

        self.workflow_checkboxes: list[ttk.Checkbutton] = []
        self.workflow_checkboxes_values: list[tuple[str, BooleanVar]] = []
        checkbox_counter = 0
        for workflow_name in config.WORKFLOW_NAMES:
            workflow_value = BooleanVar(self)
            workflow_value.set(False)
            self.workflow_checkboxes_values.append((workflow_name, workflow_value))

            workflow_checkbox = ttk.Checkbutton(
                self,
                text=workflow_name,
                variable=workflow_value,
                command=self.any_state_change,
            )
            workflow_checkbox.place(x=20, y=280 + 35 * checkbox_counter)
            self.workflow_checkboxes.append(workflow_checkbox)

            checkbox_counter += 1

        self.place(width=800, height=800)

        self.plan_button = ttk.Button(text="PLAN", command=self.plan_selected)
        self.plan_button.place(x=300, y=300 + 35 * checkbox_counter)
        self.style = get_style()

        self.deploy_button = ttk.Button(
            text="DEPLOY",
            command=self.deploy_selected,
            state="disabled",
            style="TButton",
        )
        self.deploy_button.place(x=450, y=300 + 35 * checkbox_counter)

        self.place(width=800, height=400 + 35 * checkbox_counter)
        main_window.minsize(1000, 400 + 35 * checkbox_counter)

    def any_state_change(self):
        self.deploy_button.config(state="disabled")

    def plan_selected(self):
        logger.info("Planning selected componets")
        request_form = {"target_env": self.environment_box.get()}

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

            logger.info(f"Workflow {workflow_checkbox.cget('text')} is selected")
            request_form["workflows"].append(workflow_checkbox.cget("text"))

        self.plan_status = plan_all(request_form)
        if self.plan_status == "success":
            self.deploy_button.config(state="normal")

            self.request_form = request_form

    def deploy_selected(self):
        logger.info("Deploying selected componets")
        if self.plan_status == "success":
            deploy_all(self.request_form)


def run_app_for_plan_and_deploy():
    main_window = Tk()
    app = Application(main_window)
    app.mainloop()
