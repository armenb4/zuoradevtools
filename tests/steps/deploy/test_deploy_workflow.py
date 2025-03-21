from pytest_mock import MockerFixture
from common.lib.logger import logger
from steps.deploy.workflow import deploy_workflow, deploy_all_workflows


def test_deploy_workflow():
    deploy_workflow(
        environment="dev",
        workflow_name="Publish Payment Apply Unapply Instructions",
    )


def test_deply_all_workflows(mocker: MockerFixture):
    def mocked_deploy_workflow(*args, **kwargs):
        logger.info("Mocked deploy_workflow")

    mocker.patch(
        "common.deploy.workflow.deploy_workflow",
        side_effect=mocked_deploy_workflow,
    )

    deploy_all_workflows(
        environment="dev",
        workflow_names=[
            "Workflow name 1",
            "Workflow name 2",
            "Workflow name 3",
        ],
    )
