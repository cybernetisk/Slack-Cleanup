import pytest
import cfg as cnf


@pytest.fixture(autouse=True, scope="session")
def config():
    return cnf.config


@pytest.fixture(autouse=True, scope="session")
def auth():
    return cnf.auth
