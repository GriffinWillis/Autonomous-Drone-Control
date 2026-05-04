import pytest


@pytest.fixture()
def expected_greeting() -> str:
    return "Hello, production-ready world!\n"
