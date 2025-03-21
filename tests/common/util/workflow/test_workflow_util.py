from common.lib.logger import logger
from common.util.workflow.util import ZuoraWorkflowUtil


def test_get_workflow_version_map():
    version_map = ZuoraWorkflowUtil.get_workflow_version_map_by_workflow_name(
        environment="dev",
        workflow_name="Publish Payment Apply Unapply Instructions",
    )

    logger.info(version_map)


def test_create_new_version_tag():
    version_map = {
        "1.0.1": 1234,
        "1.2.0": 1234,
        "2.0.1": 1234,
        "0.0.9": 1234,
    }

    new_version = ZuoraWorkflowUtil.get_new_version_tag(version_map)

    assert new_version == "2.0.2"


def test_get_target_workflow_id_and_version():
    workflow_id, new_version = ZuoraWorkflowUtil.get_target_workflow_id_and_version(
        environment="dev",
        workflow_name="Publish Payment Apply Unapply Instructions",
    )

    assert workflow_id == 480329
    assert new_version == "0.0.4"
