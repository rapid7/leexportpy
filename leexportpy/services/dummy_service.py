import logging

import requests

from leexportpy.service import Service

logger = logging.getLogger(__name__)


class DummyService(Service):
    def __init__(self, data, api_key, destination_config):
        super(DummyService, self).__init__(data, api_key, destination_config)

    def transform(self):
        return {'payload': self.data}

    def push(self, payload):
        push_url = self.destination_config.get('push_url')
        logger.info("This is my push url: %s", push_url)
        logger.info("This is my api_key: %s", self.api_key)
        logger.info("This is my payload: %s", payload)
        logger.info("What else does a service needs to be pushed?")
        requests.put(push_url, payload)

    def process(self):
        self.push(self.transform())
