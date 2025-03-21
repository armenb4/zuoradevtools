def sanitize_input(input: str) -> str:
    return input.replace("/^(\.\.(\/|\\|$))+/", "")
