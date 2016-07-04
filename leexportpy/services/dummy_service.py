import logging

import requests

from leexportpy.service import Service

LOGGER = logging.getLogger(__name__)


class DummyService(Service):
    """
    En example service class to show how to provide a new service support.
    """
    def __init__(self, response, api_key, destination_config):
        """
        Initialize DummyService
        """
        super(DummyService, self).__init__(response, api_key, destination_config)

    def _transform(self):
        """
        Transform DummyService data.
        """
        return {'payload': self.response}

    def _push(self, payload):
        """
        Push DummyService data.
        """
        push_url = self.destination_config.get('push_url')
        LOGGER.info("This is my push url: %s", push_url)
        LOGGER.info("This is my api_key: %s", self.api_key)
        LOGGER.info("This is my payload: %s", payload)
        LOGGER.info("What else does a service needs to be pushed?")
        requests.put(push_url, payload)

    def process(self):
        """
        Process DummyService. Transform and push.
        """
        self._push(self._transform())
