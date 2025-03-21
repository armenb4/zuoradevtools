from steps.deploy.custom_objects_records import deploy_all_custom_object_records


def test_deploy_all_custom_object_records():
    deploy_all_custom_object_records(environment="olduat")
