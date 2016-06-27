import logging
import time

import datetime
import requests

from leexportpy.service import Service

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'

logger = logging.getLogger(__name__)


class HostedGraphiteService(Service):
    def __init__(self, data, api_key, search):
        Service.__init__(self, data, api_key, search)

    def process(self):
        self.push(self.transform())

    def push(self, payload):
        if super(HostedGraphiteService, self).push(payload):    # payload is not none
            push_url = self.destination_config.get('push_url')
            resp = requests.put(push_url, auth=(self.api_key, ''), data=payload)
            logger.info("Payload to be pushed: %s", payload)
            logger.info("Response code: %d", resp.status_code)
            logger.debug("Response text: %s", resp.text)
        else:
            logger.warning("Payload is None")

    @staticmethod
    def convert_datetime_to_timestamp(date):
        return time.mktime(datetime.datetime.strptime(date, DATEFORMAT).timetuple())

    def transform(self):
        x_axis = self.data.get_keys()
        values = self.data.get_values()
        data = ""
        for i in range(self.data.get_data_length()):
            item = self.destination_config.get('metric_name') + " " + str(values[i]) + " " + str(
                int(self.convert_datetime_to_timestamp(x_axis[i]))) + "\n"
            data += item

        return data
