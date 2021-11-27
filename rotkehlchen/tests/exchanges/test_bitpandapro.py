import json
import warnings as test_warnings
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests

from rotkehlchen.exchanges.bitpandapro import BitpandaPro
from rotkehlchen.tests.utils.mock import MockResponse
from rotkehlchen.typing import Location


def test_name():
    exchange = BitpandaPro('bitpandapro1', 'a', b'a', object(), object())
    assert exchange.location == Location.BITPANDAPRO
    assert exchange.name == 'bitpandapro1'


BALANCE_RESPONSE="""
"""


def test_balances_succeeds(mock_bitpandapro: BitpandaPro):
    def mock_bitpandapro_query(url: str, **kwargs):  # pylint: disable=unused-argument
        if '/account/balances' in url:
            return MockResponse(status_code=HTTPStatus.OK, text=BALANCE_RESPONSE)
        # else
        raise AssertionError(f'Unexpected url {url} in bitpanda test')

    with patch.object(mock_bitpandapro.session, 'get', side_effect=mock_bitpandapro_query):
        balances, msg = mock_bitpandapro.query_balances()

    warnings = mock_bitpandapro.msg_aggregator.consume_warnings()
    errors = mock_bitpandapro.msg_aggregator.consume_errors()
    assert len(warnings) == 0
    assert len(errors) == 0
    assert len(msg) == 0
