import json

import datetime

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'


class QueryResponse(object):
    """
    Base class to handle event and statistics responses.
    """
    def __init__(self, data):
        """
        Initialize query response
        """
        self.data = data

    @classmethod
    def is_events(cls, data):
        """
        Is events query or not
        """
        return data.get('events') is not None

    @classmethod
    def is_statistics(cls, data):
        """
        Is statistics query or not
        """
        return data.get('statistics') is not None


class StatisticsResponse(QueryResponse):
    """
    Base class to handle GroupBy and Timeseries query results.
    """
    def __init__(self, data):
        """
        Initialize statistics query
        """
        super(StatisticsResponse, self).__init__(data)
        self.leql = QueryLeql(self.data['leql']['during']['from'],
                              self.data['leql']['during']['to'],
                              self.data['leql']['statement'])
        self.statistics = self.data['statistics']

    def get_granularity(self):
        """
        Get granularity of statistics
        """
        return self.statistics['granularity']

    def get_count(self):
        """
        Get count of statistics
        """
        return self.statistics['count']

    def get_from(self):
        """
        Get 'from' timestamp of query
        """
        return self.statistics['from']

    def get_to(self):
        """
        Get 'to' timestamp of query
        """
        return self.statistics['to']

    @classmethod
    def is_groupby(cls, data):
        """
        Is it a group by response or not
        """
        groups = data['statistics'].get('groups')
        return groups is not None and len(groups) != 0

    @classmethod
    def is_timeseries(cls, data):
        """
        Is it a timeseries response or not
        """
        statistics = data['statistics'].get('timeseries')
        return statistics is not None and len(statistics) != 0

    def get_data_length(self):
        """
        Abstract method - Get data length
        """
        raise NotImplementedError("Call to abstract method")

    def get_keys(self):
        """
        Abstract method - Get keys
        """
        raise NotImplementedError("Call to abstract method")

    def get_values(self):
        """
        Abstract method - Get values
        """
        raise NotImplementedError("Call to abstract method")

    def to_json(self):
        """
        Convert statistics response to json.
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)


class TimeSeriesStatisticsResponse(StatisticsResponse):
    """
    Class that handles timeseries results of REST API.
    """
    def __init__(self, data):
        """
        Initialize timeseries statistics response
        """
        super(TimeSeriesStatisticsResponse, self).__init__(data)

    def get_timeseries(self):
        """
        Get timeseries results
        """
        key = self.statistics['timeseries'].keys()[0]
        return self.statistics['timeseries'].get(key)

    def get_count(self):
        """
        Get global count of timeseries result
        """
        return self.statistics['stats']['global_timeseries']['count']

    def get_data_length(self):
        """
        Get timeseries data length
        """
        return len(self.get_timeseries())

    def get_keys(self):
        """
        Get keys of timeseries
        """
        number_of_points = self.get_data_length()
        granularity = self.get_granularity()
        start = self.get_from()
        keys = [self.convert_timestamp_to_str(start)]
        point = start
        for i in range(1, number_of_points):
            point = int(point) + granularity
            date = self.convert_timestamp_to_str(point)
            keys.append(date)
        return keys

    def get_values(self):
        """
        Get values of timeseries
        """
        values = []
        for i in range(self.get_data_length()):
            key = self.get_timeseries()[i].keys()[0]
            values.append(self.get_timeseries()[i][key])
        return values

    @staticmethod
    def convert_timestamp_to_str(timestamp):
        """
        Convert given timestamp to date string in the given format.
        """
        return datetime.datetime.fromtimestamp(int(timestamp) / 1000).strftime(DATEFORMAT)


class GroupByStatisticsResponse(StatisticsResponse):
    """
    Class that handles group by results of REST API.
    """
    def __init__(self, data):
        """
        Initialize group by statistics response
        """
        super(GroupByStatisticsResponse, self).__init__(data)

    def get_groups(self):
        """
        Get groups da
        """
        return self.statistics['groups']

    def get_data_length(self):
        """
        Get groups length
        """
        return len(self.get_groups())

    def get_keys(self):
        """
        Get keys of group by response
        """
        keys = []
        for i in range(self.get_data_length()):
            key = str(self.get_groups()[i].keys()[0])
            keys.append(key)
        return keys

    def get_values(self):
        """
        Get values of group by response
        """
        values = []
        for i in range(self.get_data_length()):
            group = str(self.get_groups()[i].keys()[0])
            key = self.get_groups()[i][group].keys()[0]
            values.append(self.get_groups()[i][group][key])
        return values


class QueryLeql(object):
    """
    LEQL class that maps to LEQL data in responses.
    """
    def __init__(self, from_timestamp, to_timestamp, statement):
        """
        Initialize LEQL
        """
        self.during = {'from': from_timestamp, 'to': to_timestamp}
        self.statement = statement

    def to_json(self):
        """
        Convert LEQL to json.
        """
        return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
