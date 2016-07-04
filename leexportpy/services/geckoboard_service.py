import json
import logging

import requests

from leexportpy.queryresponse import QueryResponse, StatisticsResponse, \
    TimeSeriesStatisticsResponse, GroupByStatisticsResponse
from leexportpy.service import Service

LOGGER = logging.getLogger(__name__)


class GeckoboardService(Service):
    """
    Geckoboard Service class.
    """

    def __init__(self, response, api_key, destination_config):
        """
        Initialize Geckoboard service.

        :param response:            data to be transformed
        :param api_key:             api key for 3rd party endpoint.
        :param destination_config:  destination config of search.
        """
        super(GeckoboardService, self).__init__(response, api_key, destination_config)

    def process(self):
        """
        Process service with related data, api key and config. Transform and push.
        """
        geckoboard_data = self._transform()
        self._push(geckoboard_data)

    def _push(self, payload):
        """
        Push transformed data.
        """
        if super(GeckoboardService, self)._push(payload):  # payload is not none
            push_url = self.destination_config.get('push_url')
            payload["api_key"] = self.api_key
            push = requests.post(push_url, json.dumps(payload))
            LOGGER.info("Json to be pushed: %s", json.dumps(payload))
            LOGGER.info("Response code: %d", push.status_code)
            LOGGER.debug("Response text: %s", push.text)
        else:
            LOGGER.warning("Payload is None")

    def _transform(self):
        """
        Transform data to related geckoboard widget data in destination_config
        """
        widget_type = self.destination_config.get("widget_type")
        if widget_type == 'bar_chart':
            return self.format_bar_chart_data()
        elif widget_type == 'pie_chart':
            return self.format_pie_chart_data()
        elif widget_type == 'line_chart':
            return self.format_line_chart_data()
        elif widget_type == 'number_stat':
            return self.format_number_stat_data()

    def format_line_chart_data(self):
        """
        Convert query response to geckoboard line chart data.
        """
        if QueryResponse.is_statistics(self.response):
            if StatisticsResponse.is_timeseries(self.response):
                timeseries_response = TimeSeriesStatisticsResponse(self.response)
                timeseries = timeseries_response.get_timeseries()
                x_axis = timeseries_response.get_keys()
                formatted_data = [{"name": self.destination_config.get('name'), "data": []}]
                for index, item in enumerate(timeseries):
                    key = item.keys()[0]
                    formatted_data[0]["data"].append([x_axis[index], item[key]])

                line_chart_json = {"data": {"x_axis": {"type": "datetime"}, "series": []}}
                line_chart_json["data"]["series"] = formatted_data
                return line_chart_json
            else:
                LOGGER.warn(
                    'Response does not contain timeseries result. Geckoboard line chart needs '
                    'timeseries result.')
        else:
            LOGGER.warn('Response does not contain statistics result, geckoboard pie chart needs '
                        'statistics.')
            return None

    def format_pie_chart_data(self):
        """
        Convert query response to geckoboard pie chart data.
        """
        if QueryResponse.is_statistics(self.response):
            if StatisticsResponse.is_groupby(self.response):
                groupby_response = GroupByStatisticsResponse(self.response)

                formatted_data = []
                LOGGER.debug('Size of group array: %i', len(groupby_response.get_groups()))

                for item in groupby_response.get_groups():
                    label = str(item.keys()[0])
                    value = item[label]['count']
                    LOGGER.debug('key/value is: %s, %i', label, value)
                    formatted_data.append({"label": label, "value": value})

                pie_chart_data = {"data": {"item": []}}
                pie_chart_data["data"]["item"] = formatted_data
                return pie_chart_data
            else:
                LOGGER.warn('Response does not contain groupby result. Geckoboard pie chart '
                            'needs groupby result.')
                return None
        else:
            LOGGER.warn('Response does not contain statistics result, geckoboard pie chart needs '
                        'statistics.')
            return None

    def format_bar_chart_data(self):
        """
        Convert query response to bar chart data.
        """
        if QueryResponse.is_statistics(self.response):
            if StatisticsResponse.is_timeseries(self.response):
                response_object = TimeSeriesStatisticsResponse(self.response)
            elif StatisticsResponse.is_groupby(self.response):
                response_object = GroupByStatisticsResponse(self.response)
            else:
                LOGGER.warn('Response contains neither timeseries nor groupby result. Geckoboard '
                            'bar chart needs either of them.')
                return None

            keys = response_object.get_keys()
            values = response_object.get_values()
            return {'data': {'x_axis': {'labels': keys, 'type': 'datetime'},
                             'y_axis': {'format': 'decimal'},
                             'series': [{'data': values}]}}
        else:
            LOGGER.warn('Response does not contain statistics result, geckoboard bar chart needs '
                        'statistics.')
            return None

    def format_number_stat_data(self):
        """
        Convert query response to number stat data.
        """
        if QueryResponse.is_statistics(self.response):
            if StatisticsResponse.is_timeseries(self.response):
                timeseries_response = TimeSeriesStatisticsResponse(self.response)

                count = timeseries_response.get_count()
                LOGGER.debug("Number stat data count: %i", count)
                return {"data": {
                    "item": [{"value": count, "text": self.destination_config.get('text')}]}}
            else:
                LOGGER.warn(
                    'Response does not contain timeseries result. Geckoboard number stat widget '
                    'needs timeseries result.')
            return None
        else:
            LOGGER.warn('Response does not contain statistics result, geckoboard number stat '
                        'widget needs statistics.')
            return None
