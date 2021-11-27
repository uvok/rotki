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
{
    "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
    "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
    "balances": [
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "BEST",
            "change": "0.1",
            "available": "20.0",
            "locked": "4.0",
            "sequence": 400,
            "time": "2021-11-16T17:36:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "BTC",
            "change": "0.0001",
            "available": "0.0028",
            "locked": "0.006",
            "sequence": 500,
            "time": "2021-11-23T17:04:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "CHZ",
            "change": "250",
            "available": "0.0",
            "locked": "0.0",
            "sequence": 600,
            "time": "2021-11-03T09:36:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "DOGE",
            "change": "600.0",
            "available": "0.8",
            "locked": "611.0",
            "sequence": 700,
            "time": "2021-11-16T17:13:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "DOT",
            "change": "1.0",
            "available": "0.00004",
            "locked": "3.0",
            "sequence": 800,
            "time": "2021-11-16T17:12:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "ETH",
            "change": "0.02",
            "available": "0.00005",
            "locked": "0.08",
            "sequence": 900,
            "time": "2021-11-23T17:06:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "EUR",
            "change": "149.0",
            "available": "41.655",
            "locked": "0.0",
            "sequence": 1000,
            "time": "2021-11-16T17:36:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "LINK",
            "change": "4.0",
            "available": "0.0",
            "locked": "4.70",
            "sequence": 1100,
            "time": "2021-11-16T17:13:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "LTC",
            "change": "0.0",
            "available": "0.000008",
            "locked": "0.0",
            "sequence": 1200,
            "time": "2021-11-10T21:43:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "MIOTA",
            "change": "100.0",
            "available": "0.0",
            "locked": "0.0",
            "sequence": 1300,
            "time": "2021-05-18T06:05:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "PAN",
            "change": "10.0",
            "available": "0.0",
            "locked": "0.0",
            "sequence": 1400,
            "time": "2021-11-04T09:58:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "XLM",
            "change": "0.0",
            "available": "0.0",
            "locked": "0.0",
            "sequence": 1500,
            "time": "2021-05-16T13:37:00.000000Z"
        },
        {
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "account_holder": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "currency_code": "XRP",
            "change": "200.0",
            "available": "0.5",
            "locked": "300.0",
            "sequence": 1600,
            "time": "2021-11-23T17:05:00.000000Z"
        }
    ]
}
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
