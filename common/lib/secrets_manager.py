import os
import json
import boto3
from pathlib import Path
from boto3_type_annotations.secretsmanager import Client as SMClient
from common.lib.logger import logger


IS_LOCAL = os.getenv("IS_LOCAL", True)
IS_AWS_HOSTED = os.getenv("IS_AWS_HOSTED", False)

if IS_AWS_HOSTED:
    SECRETS_PATHS = {
        "dev": "/applications/dev/dev/zuora-devtools",
        "qa": "/applications/dev/itb/zuora-devtools",
        "uat": "/applications/qa/qa/zuora-devtools",
        "prod": "/applications/prod/prod/zuora-devtools",
    }
else:
    SECRETS_PATHS = {
        "dev": "dev",
        "qa": "qa",
        "uat": "uat",
        "prod": "prod",
    }


sm_client: SMClient = boto3.client(
    service_name="secretsmanager",
    region_name="us-east-1",
)
local_sm_file = Path.home().joinpath(".zuora/sm.json")


class SecretsManager:
    @staticmethod
    def get_secrets_path_for_environment(
        secrets_path: str = None, environment: str = None
    ) -> str:
        if not secrets_path and not environment:
            raise ValueError(
                "Missing arguments: either secrets_path or environment should have a valid value"
            )

        if environment and not secrets_path:
            secrets_path = SECRETS_PATHS.get(environment.lower())

        if not secrets_path:
            raise ValueError(f"Not valid secrets_path {secrets_path}")

        return secrets_path

    @staticmethod
    def get_secret(
        secret_key: str, secrets_path: str = None, environment: str = None
    ) -> str:
        """Get a specific secret by key from secrets paths"""
        secrets_path = SecretsManager.get_secrets_path_for_environment(
            secrets_path=secrets_path,
            environment=environment,
        )

        secrets = SecretsManager.get_secrets(secrets_path)
        return secrets.get(secret_key, None)

    @staticmethod
    def get_secrets(secrets_path: str) -> dict:
        """Get secrets from Secrets Manager

        Args:
            secrets_path (str): Secret Name stored in Secrets manager

        Returns:
            dict: key-value pair stored in the Secret name in Secrets manager
        """
        if IS_LOCAL:
            with open(local_sm_file) as fs:
                all_secrets = json.load(fs)
                return all_secrets[secrets_path]

        try:
            get_secret_value_response = sm_client.get_secret_value(
                SecretId=secrets_path
            )
        except Exception as e:
            msg = f"ERROR: Resource {secrets_path} not found in Secrets Manager. \n{e}"
            logger.exception(msg)
            raise Exception(msg)

        secrets_str = get_secret_value_response["SecretString"]
        secrets: dict = json.loads(secrets_str)
        return secrets

    @staticmethod
    def update_secret(
        secret: dict, secrets_path: str = None, environment: str = None
    ) -> None:
        """Update key-value pair in secrets manager

        Args:
            secret (dict): key-value dict to be updated in Secrets Manager
            secrets_path (str): Secret Name stored in Secrets Manager
        """
        secrets_path = SecretsManager.get_secrets_path_for_environment(
            secrets_path=secrets_path,
            environment=environment,
        )

        if IS_LOCAL:
            with open(local_sm_file) as fs:
                all_secrets = json.load(fs)

            for key, value in secret.items():
                all_secrets[secrets_path][key] = value

            with open(local_sm_file, "w") as fs:
                json.dump(all_secrets, fs, indent=4)

            return

        try:
            logger.info("Updating following secrets in SecretsManager")
            logger.info(f"Secret keys == {secret.keys()}")

            update_secret_response = sm_client.update_secret(
                SecretId=secrets_path, SecretString=json.dumps(secret)
            )
            logger.info(f"update_secret_response == {update_secret_response}")
        except Exception as e:
            msg = f"ERROR: Failed to update secret in Secrets Manager. \n{e}"
            logger.exception(msg)
            raise Exception(msg)
