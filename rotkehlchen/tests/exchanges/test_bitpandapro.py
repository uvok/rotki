import json
import warnings as test_warnings
from http import HTTPStatus
from unittest.mock import patch

import pytest
import requests

from rotkehlchen.exchanges.bitpandapro import BitpandaPro
