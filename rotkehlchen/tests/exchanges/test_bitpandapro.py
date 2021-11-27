import json
import warnings as test_warnings
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests

from rotkehlchen.exchanges.bitpandapro import BitpandaPro
from rotkehlchen.typing import Location

def test_name():
    exchange = BitpandaPro('bitpandapro1', 'a', b'a', object(), object())
    assert exchange.location == Location.BITPANDAPRO
    assert exchange.name == 'bitpandapro1'
