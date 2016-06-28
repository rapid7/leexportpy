import json

import datetime

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'


# this module is still in development and not in use in any other place in leexportpy.
class QueryResponse(object):
    def __init__(self, logs, metadata, statistics):
        """

        :type logs: list
        :type metadata: dict
        :type statistics: dict
        """
        self.logs = logs
        self.leql = QueryLeql(metadata['during']['from'], metadata['during']['to'],
                              metadata['statement'])
        self.statistics = statistics

    def get_count(self):
        return self.statistics['count']

    def get_keys(self):
        raise NotImplementedError("Call to abstract method")

    def get_values(self):
        raise NotImplementedError("Call to abstract method")

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class TimeseriesQueryResponse(QueryResponse):
    def __init__(self, logs, metadata, statistics):
        """

        :type statistics: dict
        :type metadata: dict
        :type logs: list
        """
        super(TimeseriesQueryResponse, self).__init__(logs, metadata, statistics)

    def get_timeseries(self):
        key = self.statistics['timeseries'].keys()[0]
        return self.statistics['timeseries'].get(key)

    def get_data_length(self):
        return len(self.get_timeseries())

    def get_granularity(self):
        return self.statistics['granularity']

    def get_keys(self):
        number_of_points = self.get_data_length()
        granularity = self.get_granularity()
        start = self.leql.during.get('from')
        x_axis = [self.convert_timestamp_to_str(start)]
        point = start
        for i in range(1, number_of_points):
            point = int(point) + granularity
            date = self.convert_timestamp_to_str(point)
            x_axis.append(date)
        return x_axis

    def get_values(self):
        values = []
        for i in range(self.get_data_length()):
            key = self.get_timeseries()[i].keys()[0]
            values.append(self.get_timeseries()[i][key])
        return values

    @staticmethod
    def convert_timestamp_to_str(timestamp):
        return datetime.datetime.fromtimestamp(int(timestamp) / 1000).strftime(DATEFORMAT)


class GroupbyQueryResponse(QueryResponse):
    def __init__(self, logs, metadata, statistics):
        """

        :type statistics: dict
        :type metadata: dict
        :type logs: list
        """
        super(GroupbyQueryResponse, self).__init__(logs, metadata, statistics)

    def get_groups(self):
        return self.statistics['groups']

    def get_data_length(self):
        return len(self.get_groups())

    def get_keys(self):
        groups = []
        for i in range(self.get_data_length()):
            label = str(self.get_groups()[i].keys()[0])
            groups.append(label)
        return groups

    def get_values(self):
        values = []
        for i in range(self.get_data_length()):
            label = str(self.get_groups()[i].keys()[0])
            key = self.get_groups()[i][label].keys()[0]
            values.append(self.get_groups()[i][label][key])
        return values


class QueryLeql(object):
    def __init__(self, from_ts, to_ts, statement):
        """

        :type statement: str
        :type to_ts: int
        :type from_ts: int
        """
        self.during = {'from': from_ts, 'to': to_ts}
        self.statement = statement

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
