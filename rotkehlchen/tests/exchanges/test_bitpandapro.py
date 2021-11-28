import json
import warnings as test_warnings
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests
from rotkehlchen.assets.asset import Asset

import rotkehlchen.constants.assets as rota
from rotkehlchen.exchanges.bitpandapro import BitpandaPro
from rotkehlchen.fval import FVal
from rotkehlchen.tests.utils.mock import MockResponse
from rotkehlchen.typing import Location


def test_name():
    exchange = BitpandaPro('bitpandapro1', 'a', b'a', object(), object())
    assert exchange.location == Location.BITPANDAPRO
    assert exchange.name == 'bitpandapro1'


BALANCE_RESPONSE = """
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
            "available": "0.0",
            "locked": "0.006",
            "sequence": 500,
            "time": "2021-11-23T17:04:00.000000Z"
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
            "currency_code": "MIOTA",
            "change": "100.0",
            "available": "10.0",
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

    assert len(balances) == 4
    assert rota.A_BEST in balances
    assert balances[rota.A_BEST].amount == FVal("20.0") + FVal("4.0")
    assert rota.A_BTC in balances
    assert balances[rota.A_BTC].amount == FVal("0.006")
    assert rota.A_EUR in balances
    assert balances[rota.A_EUR].amount == FVal("41.655")
    iota = Asset("IOTA")
    assert iota in balances
    assert balances[iota].amount == FVal("10.0")
    # no known asset, only via hash
    # assert Asset("PAN") in balances

MOCK_DEPOSITS_RESPONSE_P1 = """
{
    "max_page_size": 2,
    "cursor": "foobar",
    "deposit_history": [
        {
            "transaction_id": "ffffffff-eeee-dddd-cccc-000000000000",
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "time": "2021-06-01T16:44:26.000000Z",
            "currency": "EUR",
            "funds_source": "EXTERNAL",
            "type": "FIAT",
            "amount": "160.0",
            "fee_amount": "2.4",
            "fee_currency": "EUR"
        },
        {
            "transaction_id": "ffffffff-eeee-dddd-cccc-000000000001",
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "time": "2021-05-25T16:38:31.000000Z",
            "currency": "EUR",
            "funds_source": "EXTERNAL",
            "type": "FIAT",
            "amount": "26.6",
            "fee_amount": "0.4",
            "fee_currency": "EUR"
        }
    ]
}
"""

MOCK_DEPOSITS_RESPONSE_P2 = """
{
    "deposit_history": [
        {
            "transaction_id": "ffffffff-eeee-dddd-cccc-000000000002",
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "time": "2021-04-02T11:27:31.000000Z",
            "currency": "DOGE",
            "funds_source": "INTERNAL",
            "type": "CRYPTO",
            "amount": "25000.0",
            "fee_amount": "0.0",
            "fee_currency": "DOGE"
        }
    ]
}
"""

MOCK_WITHDRAWALS_RESPONSE = """
{
    "withdrawal_history": [
        {
            "transaction_id": "ffffffff-eeee-dddd-cccc-000000000003",
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "time": "2021-10-16T15:01:19.000000Z",
            "currency": "EUR",
            "funds_source": "EXTERNAL",
            "type": "FIAT",
            "amount": "400.0",
            "fee_amount": "0.0",
            "fee_currency": "EUR"
        },
        {
            "transaction_id": "ffffffff-eeee-dddd-cccc-000000000004",
            "account_id": "ffffffff-eeee-dddd-cccc-bbbbbbbbbbbb",
            "time": "2021-04-05T19:15:11.000000Z",
            "currency": "EUR",
            "funds_source": "EXTERNAL",
            "type": "FIAT",
            "amount": "500.0",
            "fee_amount": "0.0",
            "fee_currency": "EUR"
        }
    ]
}
"""

def test_query_online_deposits_withdrawals(mock_bitpandapro: BitpandaPro):
    deposit_pagecount = 0
    # test cursor handling as well
    def mock_bitpandapro_query(url: str, **kwargs):  # pylint: disable=unused-argument
        nonlocal deposit_pagecount
        if '/account/deposits' in url:
            if deposit_pagecount == 0:
                response = MockResponse(status_code=HTTPStatus.OK, text=MOCK_DEPOSITS_RESPONSE_P1)
            elif deposit_pagecount == 1:
                if "cursor=foobar" in url:
                    response = MockResponse(status_code=HTTPStatus.OK, text=MOCK_DEPOSITS_RESPONSE_P2)
                else:
                    raise AssertionError(f'Invalid cursor')
            else:
                raise AssertionError(f'Too many pages fetched')
            deposit_pagecount += 1
            return response
        elif '/account/withdrawals' in url:
            return MockResponse(status_code=HTTPStatus.OK, text=MOCK_WITHDRAWALS_RESPONSE)
        # else
        raise AssertionError(f'Unexpected url {url} in bitpanda test')

    with patch.object(mock_bitpandapro.session, 'get', side_effect=mock_bitpandapro_query):
        movements = mock_bitpandapro.query_online_deposits_withdrawals(0, 0)
