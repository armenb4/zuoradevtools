import pytest
from common.lib.secrets_manager import SecretsManager


def test_get_non_existing_secrets():
    secrets_path = "/applications/dev/dev/invalidsecret"

    with pytest.raises(Exception):
        SecretsManager.get_secrets(secrets_path)


def test_get_existing_secrets():
    secrets_path = "/applications/dev/dev/zuora-devtools"

    secrets = SecretsManager.get_secrets(secrets_path)

    secret_keys = list(secrets.keys())
    assert "zuora_client_id" in secret_keys
    assert "zuora_client_secret" in secret_keys
