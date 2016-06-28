import json
import logging

import requests

from leexportpy.service import Service

LOGGER = logging.getLogger(__name__)


class GeckoboardService(Service):
    """
    Geckoboard Service class.
    """

    def __init__(self, data, api_key, destination_config):
        """
        Initialize Geckoboard service.

        :param data:                data to be transformed
        :param api_key:             api key for 3rd party endpoint.
        :param destination_config:  destination config of search.
        """
        super(GeckoboardService, self).__init__(data, api_key, destination_config)

    def process(self):
        """
        Process service with related data, api key and config. Transform and push.
        """
        geckoboard_data = self.transform()
        self.push(geckoboard_data)

    def push(self, payload):
        """
        Push transformed data.
        """
        if super(GeckoboardService, self).push(payload):  # payload is not none
            push_url = self.destination_config.get('push_url')
            payload["api_key"] = self.api_key
            push = requests.post(push_url, json.dumps(payload))
            LOGGER.info("Json to be pushed: %s", json.dumps(payload))
            LOGGER.info("Response code: %d", push.status_code)
            LOGGER.debug("Response text: %s", push.text)
        else:
            LOGGER.warning("Payload is None")

    def transform(self):
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
        data = self.data.get_data()
        x_axis = self.data.get_keys()
        formatted_data = [{"name": self.destination_config.get('name'), "data": []}]
        for index, item in enumerate(data):
            key = item.keys()[0]
            formatted_data[0]["data"].append([x_axis[index], item[key]])

        line_chart_json = {"data": {"x_axis": {"type": "datetime"}, "series": []}}
        line_chart_json["data"]["series"] = formatted_data
        return line_chart_json

    def format_pie_chart_data(self):
        """
        Convert query response to geckoboard pie chart data.
        """
        data = self.data.get_data()
        formatted_data = []
        LOGGER.debug('Size of group array: %i', len(data))

        for item in data:
            label = str(item.keys()[0])
            value = item[label]['count']
            LOGGER.debug('key/value is: %s, %i', label, value)
            formatted_data.append({"label": label, "value": value})

        pie_chart_data = {"data": {"item": []}}
        pie_chart_data["data"]["item"] = formatted_data
        return pie_chart_data

    def format_bar_chart_data(self):
        """
        Convert query response to bar chart data.
        """
        keys = self.data.get_keys()
        values = self.data.get_values()
        return {'data': {'x_axis': {'labels': keys, 'type': 'datetime'},
                         'y_axis': {'format': 'decimal'},
                         'series': [{'data': values}]}}

    def format_number_stat_data(self):
        """
        Convert query response to number stat data.
        """
        count = self.data.get_statistics_count()
        LOGGER.debug("Number stat data count: %i", count)
        return {"data": {"item": [{"value": count, "text": self.destination_config.get('text')}]}}
