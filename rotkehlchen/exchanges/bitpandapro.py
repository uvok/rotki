import logging

from typing import TYPE_CHECKING

from rotkehlchen.exchanges.exchange import ExchangeInterface
from rotkehlchen.logging import RotkehlchenLogsAdapter
from rotkehlchen.typing import ApiKey, ApiSecret, Location
from rotkehlchen.user_messages import MessagesAggregator

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
