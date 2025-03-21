from datetime import datetime
from common.app.zuora.api import ZuoraAPI
from common.lib.secrets_manager import SecretsManager


def test_zuoraapi_init_dev_env():
    zuora_api = ZuoraAPI(environment="DEV")

    assert zuora_api.version == SecretsManager.get_secret(
        secret_key="zuora_api_version",
        environment="DEV",
    )

    assert zuora_api.base_url == SecretsManager.get_secret(
        secret_key="zuora_api_base_url",
        environment="DEV",
    )

    assert zuora_api.token_ttl > datetime.now()


def test_zuoraapi_init_olduat_env():
    zuora_api = ZuoraAPI(environment="OLDUAT")

    assert zuora_api.version == SecretsManager.get_secret(
        secret_key="zuora_api_version",
        environment="OLDUAT",
    )

    assert zuora_api.base_url == SecretsManager.get_secret(
        secret_key="zuora_api_base_url",
        environment="OLDUAT",
    )
    assert zuora_api.token_ttl > datetime.now()


def test_zuoraapi_renew_token_if_expired():
    zuora_api = ZuoraAPI(environment="DEV")

    zuora_api.renew_bearer_token_if_expired()
