import logging
import time

import datetime
import requests

from leexportpy.queryresponse import QueryResponse, StatisticsResponse, \
    TimeSeriesStatisticsResponse
from leexportpy.service import Service

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'
LOGGER = logging.getLogger(__name__)


class HostedGraphiteService(Service):
    """
    Hosted graphite service module that defines necessary transform and push algorithms.
    """

    def __init__(self, response, api_key, destination_config):
        """
        Initialize HostedGraphiteService.
        :param response:    raw response data.
        :param api_key:     hosted graphite api key.
        :param destination_config:
        """
        super(HostedGraphiteService, self).__init__(response, api_key, destination_config)

    def process(self):
        """
        Process HostedGraphite task.
        """
        self._push(self._transform())

    def _push(self, payload):
        """
        Push payload to hosted_graphite url along with api key.

        :param payload: Data to be pushed.
        """
        if super(HostedGraphiteService, self)._push(payload):  # payload is not none
            push_url = self.destination_config.get('push_url')
            resp = requests.put(push_url, auth=(self.api_key, ''), data=payload)
            LOGGER.info("Payload to be pushed: %s", payload)
            LOGGER.info("Response code: %d", resp.status_code)
            LOGGER.debug("Response text: %s", resp.text)
        else:
            LOGGER.warning("Payload is None")

    @staticmethod
    def convert_datetime_to_timestamp(date):
        """
        Convert datetime to timestamp. Only for Hosted Graphite.

        :param date: date to be converted to timestamp.
        """
        return time.mktime(datetime.datetime.strptime(date, DATEFORMAT).timetuple())

    def _transform(self):
        """
        Transform raw data to hosted graphite data.
        """
        if QueryResponse.is_statistics(self.response):
            if StatisticsResponse.is_timeseries(self.response):
                timeseries_response = TimeSeriesStatisticsResponse(self.response)
                x_axis = timeseries_response.get_keys()
                values = timeseries_response.get_values()
                data = ""
                for i in range(timeseries_response.get_data_length()):
                    item = self.destination_config.get('metric_name') + " " \
                           + str(values[i]) + " " \
                           + str(int(self.convert_datetime_to_timestamp(x_axis[i]))) + "\n"
                    data += item
                return data
            else:
                LOGGER.warn(
                    "Expected timeseries statistics result, got groups result. Hosted graphite "
                    "accepts timeseries result. Please check your query in config file.")
                return None
        else:
            LOGGER.warn("Expected statistics result, got events result. Hosted graphite accepts "
                        "statistics result. Please check your query in config file.")
            return None
