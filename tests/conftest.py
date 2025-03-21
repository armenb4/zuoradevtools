import os
import boto3
import pytest

ENVIRONMENT = "dev"


@pytest.fixture(autouse=True)
def pre_test(request: pytest.FixtureRequest):
    print(f"\n⌛️⌛️Running test {request.node.name}")


# For local use, set AWS config profile
os.environ["ENVIRONMENT"] = ENVIRONMENT
boto3.setup_default_session(profile_name=ENVIRONMENT)
