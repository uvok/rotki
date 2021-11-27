import pytest

from rotkehlchen.tests.utils.exchanges import create_test_bitpandapro
from rotkehlchen.tests.utils.factories import make_api_key, make_api_secret


@pytest.fixture(name='bitpandapro_api_key')
def fixture_bitpanda_api_key():
    return make_api_key()


@pytest.fixture(name='bitpandapro_api_secret')
def fixture_bitpanda_api_secret():
    return make_api_secret()


@pytest.fixture
def mock_bitpandapro(
        database,
        inquirer,  # pylint: disable=unused-argument
        function_scope_messages_aggregator,
        bitpandapro_api_key,
        bitpandapro_api_secret,
):
    return create_test_bitpandapro(
        database=database,
        msg_aggregator=function_scope_messages_aggregator,
        api_key=bitpandapro_api_key,
        secret=bitpandapro_api_secret,
    )
