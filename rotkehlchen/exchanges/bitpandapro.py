import json
import logging
from collections import defaultdict

from http import HTTPStatus

from typing import TYPE_CHECKING, Any, DefaultDict, Dict, List, Optional, Tuple, Union, overload
from urllib.parse import urlencode

import gevent
import requests

from rotkehlchen.accounting.structures import Balance
from rotkehlchen.assets.asset import Asset
from rotkehlchen.constants.timing import DEFAULT_TIMEOUT_TUPLE, QUERY_RETRY_TIMES
from rotkehlchen.errors import DeserializationError, RemoteError, UnknownAsset
from rotkehlchen.exchanges.exchange import ExchangeInterface, ExchangeQueryBalances
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.typing import ApiKey, ApiSecret, Location
from rotkehlchen.user_messages import MessagesAggregator
from rotkehlchen.utils.serialization import jsonloads_dict

if TYPE_CHECKING:
    from rotkehlchen.db.dbhandler import DBHandler

logger = logging.getLogger(__name__)
log = RotkehlchenLogsAdapter(logger)

class BitpandaPro(ExchangeInterface):
    """
    Bitpanda Pro Exchange.

    Website: https://exchange.bitpanda.com/
    Docs: https://developers.bitpanda.com/exchange/
    API base: https://api.exchange.bitpanda.com/public/v1
    Websockets: wss://streams.exchange.bitpanda.com
    """
    def __init__(
            self,
            name: str,
            api_key: ApiKey,
            secret: ApiSecret,
            database: 'DBHandler',
            msg_aggregator: MessagesAggregator
    ):
        super().__init__(
            name=name,
            location=Location.BITPANDAPRO,
            api_key=api_key,
            secret=secret,
            database=database,
        )
        self.uri = 'https://api.exchange.bitpanda.com/public/v1'
        # Bitpanda Pro uses Authorization: Bearer
        self.session.headers.update({'Authorization': "Bearer " + self.api_key})

    def _api_query(
            self,
            endpoint: str,
            options: Optional[Dict[str, Any]] = None,
    ) -> Union[List[Any], Dict[str, Any]]:
        """Performs a Bitpanda Pro API Query for endpoint

        You can optionally provide extra arguments to the endpoint via the options argument.

        Returns the result data, deserialized JSON

        Raises RemoteError if something went wrong with connecting or reading from the exchange
        """
        request_url = f'{self.uri}/{endpoint}'
        retries_left = QUERY_RETRY_TIMES
        if options is not None:
            request_url += '?' + urlencode(options)
        while retries_left > 0:
            log.debug(
                'Bitpanda Pro API query',
                request_url=request_url,
                options=options,
            )
            try:
                response = self.session.get(request_url, timeout=DEFAULT_TIMEOUT_TUPLE)
            except requests.exceptions.RequestException as e:
                raise RemoteError(f'Bitpanda Pro API request failed due to {str(e)}') from e

            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                backoff_in_seconds = int(20 / retries_left)
                retries_left -= 1
                log.debug(
                    f'Got a 429 from Bitpanda Pro query of {request_url}. Will backoff '
                    f'for {backoff_in_seconds} seconds. {retries_left} retries left',
                )
                gevent.sleep(backoff_in_seconds)
                continue

            if response.status_code != HTTPStatus.OK:
                raise RemoteError(
                    f'Bitpanda Pro API request failed with response: {response.text} '
                    f'and status code: {response.status_code}',
                )

            # we got it, so break
            break

        else:  # retries left are zero
            raise RemoteError(f'Ran out of retries for Bitpanda Pro query of {request_url}')

        try:
            decoded_json = jsonloads_dict(response.text)
        except json.decoder.JSONDecodeError as e:
            raise RemoteError(f'Invalid JSON {response.text} in Bitpanda Pro response. {e}') from e

        log.debug(f'Got Bitpanda Pro response: {decoded_json}')
        return decoded_json

    def query_balances(self, **kwargs: Any) -> ExchangeQueryBalances:
        try:
            balances = self._api_query("/account/balances")
            balances = balances['balances']
        except RemoteError as e:
            msg = f'Failed to query Bitpanda Pro balances. {str(e)}'
            return None, msg

        assets_balance: DefaultDict[Asset, Balance] = defaultdict(Balance)
        return dict(assets_balance), ''
