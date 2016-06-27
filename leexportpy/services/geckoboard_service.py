import json
import logging

import requests

from leexportpy.service import Service

logger = logging.getLogger(__name__)


class GeckoboardService(Service):
    def __init__(self, data, api_key, destination_config):
        super(GeckoboardService, self).__init__(data, api_key, destination_config)

    def process(self):
        geckoboard_data = self.transform()
        self.push(geckoboard_data)

    def push(self, payload):
        if super(GeckoboardService, self).push(payload):    # payload is not none
            push_url = self.destination_config.get('push_url')
            payload["api_key"] = self.api_key
            push = requests.post(push_url, json.dumps(payload))
            logger.info("Json to be pushed: %s", json.dumps(payload))
            logger.info("Response code: %d", push.status_code)
            logger.debug("Response text: %s", push.text)
        else:
            logger.warning("Payload is None")

    def transform(self):
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
        data = self.data.get_data()
        formatted_data = []
        logger.debug('Size of group array: %i', len(data))
        for i in range(len(data)):
            label = str(data[i].keys()[0])
            value = data[i][label]['count']
            item = dict({"label": label, "value": value})
            logger.debug('key/value is: %s, %i', label, value)
            formatted_data.append(item)

        pie_chart_data = {"data": {"item": []}}
        pie_chart_data["data"]["item"] = formatted_data
        return pie_chart_data

    def format_bar_chart_data(self):
        keys = self.data.get_keys()
        values = self.data.get_values()
        return {'data': {'x_axis': {'labels': keys, 'type': 'datetime'}, 'y_axis': {'format': 'decimal'},
                         'series': [{'data': values}]}}

    def format_number_stat_data(self):
        count = self.data.get_count()
        logger.debug("Number stat data count: %i", count)
        return {"data": {"item": [{"value": count, "text": self.destination_config.get('text')}]}}
