VALID_ENVIRONMENTS = ("dev", "qa", "uat", "prod")


def validate_environment(environment: str):
    if environment.lower() not in VALID_ENVIRONMENTS:
        raise ValueError(f"Not valid environment: {environment}")
