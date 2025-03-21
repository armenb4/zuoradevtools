from pytest_mock import MockerFixture
from steps.deploy.deploy_all import deploy_all
from common.lib.logger import logger


def test_deploy_all(mocker: MockerFixture):
    def mocked_deploy_step(*args, **kwargs):
        logger.info("Using mocked step")

    mocker.patch(
        "common.deploy.deploy_all.deploy_all_workflows", side_effect=mocked_deploy_step
    )

    mocker.patch(
        "common.deploy.deploy_all.deploy_all_custom_object_records",
        side_effect=mocked_deploy_step,
    )

    deploy_all()
