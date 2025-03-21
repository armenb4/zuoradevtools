import json
import requests
import posixpath
import urllib.parse
from typing import List
from datetime import datetime, timedelta

from common.lib.logger import logger
from common.lib.secrets_manager import SecretsManager


class ZuoraAPI:
    env: str
    base_url: str
    version: str
    _bearer_token: str
    _token_ttl: datetime

    def __init__(self, environment: str):
        self.env = environment.upper()
        self.base_url = SecretsManager.get_secret(
            secret_key="zuora_api_base_url",
            environment=self.env,
        )

        self.version = SecretsManager.get_secret(
            secret_key="zuora_api_version",
            environment=self.env,
        )

        self.bearer_token = None
        self.token_ttl = None

    @property
    def bearer_token(self) -> str:
        return self._bearer_token

    @bearer_token.setter
    def bearer_token(self, token: str):
        self._bearer_token = token

    @property
    def token_ttl(self) -> int:
        return self._token_ttl

    @token_ttl.setter
    def token_ttl(self, ttl: int):
        self._token_ttl = ttl

    def generate_bearer_token(self):
        logger.info("🟡 Generating bearer token for Zuora API")
        client_id = SecretsManager.get_secret(
            secret_key="zuora_client_id",
            environment=self.env,
        )
        client_sec = SecretsManager.get_secret(
            secret_key="zuora_client_secret",
            environment=self.env,
        )
        grant_type = SecretsManager.get_secret(
            secret_key="zuora_client_grant_type",
            environment=self.env,
        )

        url = posixpath.join(self.base_url, "oauth/token")

        payload_form = {
            "client_id": client_id,
            "client_secret": client_sec,
            "grant_type": grant_type,
        }

        payload = urllib.parse.urlencode(payload_form)

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": "Bearer ",
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            response_json = response.json()
            self.bearer_token = response_json["access_token"]
            self.token_ttl = datetime.now() + timedelta(
                seconds=response_json["expires_in"]
            )
        else:
            logger.info(f"Authentication failed: \n{response.text}")
            self.bearer_token = ""
            self.token_ttl = datetime.now()

        SecretsManager.update_secret(
            secret={"zuora_bearer_token": self.bearer_token}, environment=self.env
        )
        SecretsManager.update_secret(
            secret={"zuora_token_ttl": self.token_ttl.timestamp()}, environment=self.env
        )

    def renew_bearer_token_if_expired(self):
        logger.info("Checking if token is still valid ...")
        self.bearer_token = SecretsManager.get_secret(
            secret_key="zuora_bearer_token", environment=self.env
        )
        zuora_token_ttl_timestamp = SecretsManager.get_secret(
            secret_key="zuora_token_ttl", environment=self.env
        )

        if not self.bearer_token or not zuora_token_ttl_timestamp:
            self.generate_bearer_token()
            return

        self.token_ttl = datetime.fromtimestamp(zuora_token_ttl_timestamp)
        if datetime.now() > self.token_ttl:
            self.generate_bearer_token()
        else:
            logger.info("✅ Zuora API bearer token is still valid")

    def get(self, path: str, payload: dict = {}):
        logger.info("Zuora API - GET method")

        self.renew_bearer_token_if_expired()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

        url = posixpath.join(self.base_url, path)
        response = requests.request("GET", url, headers=headers, data=payload)

        return response

    def post(self, path: str, payload: dict = {}, files: List[str] = []):
        logger.info("Zuora API - POST method")

        self.renew_bearer_token_if_expired()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

        url = posixpath.join(self.base_url, path)
        logger.info(f"url == {url}")
        logger.debug(f"payload == {payload}")

        response = requests.request(
            "POST", url, headers=headers, data=payload, files=files
        )

        return response

    def post_multipart(self, path: str, files: dict = {}):
        logger.info("Zuora API - POST multipart method")

        self.renew_bearer_token_if_expired()

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

        url = posixpath.join(self.base_url, path)
        logger.info(f"url == {url}")
        logger.info(f"files == {files}")

        response = requests.post(
            url,
            headers=headers,
            files=files,
        )

        return response

    def put(self, path: str, payload: dict = {}):
        logger.info("Zuora API - PUT method")

        self.renew_bearer_token_if_expired()

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {self.bearer_token}",
        }

        url = posixpath.join(self.base_url, path)
        logger.info(f"url == {url}")
        logger.debug(f"payload == {payload}")

        response = requests.request(
            "PUT", url, headers=headers, data=json.dumps(payload)
        )

        return response
