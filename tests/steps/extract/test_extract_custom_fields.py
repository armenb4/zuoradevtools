from steps.extract.custom_fields import extract_custom_fields_to_file


def test_extract_custom_fields_to_file():
    extract_custom_fields_to_file(environment="dev")
