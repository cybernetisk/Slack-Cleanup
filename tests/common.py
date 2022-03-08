import pytest
import cfg as cnf


@pytest.fixture(autouse=True, scope="session")
def config() -> cnf.Config:
    return cnf.config


@pytest.fixture(autouse=True, scope="session")
def auth() -> cnf.Auth:
    return cnf.auth
