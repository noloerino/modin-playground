import pytest

conf = {}

def pytest_addoption(parser):
    parser.addoption("--nostats", action="store_true", default=False)
    parser.addoption("--big", action="store_true", default=False)

# @pytest.fixture(autouse=True, scope="session")
# def check_config(pytestconfig):
#     yield

def pytest_configure(config):
    pytest.conf = conf
    conf["nostats"] = config.getoption("nostats")
    conf["big"] = config.getoption("big")
