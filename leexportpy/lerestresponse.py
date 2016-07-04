import datetime

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'


# deprecated
class LeRestResponse(object):
    """
    Helper class to wrap up response.
    """
    def __init__(self, response_json):
        self.json = response_json

    def has_groups(self):
        """
        Check response if it has groups or not
        """
        groups = self.json['statistics'].get('groups')
        return groups is not None and len(groups) != 0

    def get_logs(self):
        """
        Get logs that were queried.
        """
        return self.json.get('logs')

    def get_leql(self):
        """
        Get leql information.
        """
        return self.json.get('leql')

    def get_data(self):
        """
        Get data in the response.
        """
        if self.has_groups():
            return self.json['statistics'].get('groups')
        else:
            timeseries_key = self.json['statistics']['timeseries'].keys()[0]
            return self.json['statistics']['timeseries'].get(timeseries_key)

    def get_data_length(self):
        """
        Get data length.
        """
        return len(self.get_data())

    def get_statistics_count(self):
        """
        Get statistics data count.
        """
        return self.json['statistics'].get('count')

    def get_keys(self):
        """
        Get keys of groups or timeseries statistics.
        """
        if self.has_groups():
            groups = []
            for i in range(self.get_data_length()):
                label = str(self.get_data()[i].keys()[0])
                groups.append(label)
            return groups
        else:
            number_of_points = self.get_data_length()
            granularity = self.get_granularity()
            start = self.json['statistics']['from']
            x_axis = [datetime.datetime.fromtimestamp(int(start) / 1000).strftime(DATEFORMAT)]
            point = start
            for i in range(1, number_of_points):
                point = int(point) + granularity
                date = datetime.datetime.fromtimestamp(int(point) / 1000).strftime(DATEFORMAT)
                x_axis.append(date)
            return x_axis

    def get_values(self):
        """
        Get values of groups or timeseries statistics data.
        """
        values = []

        if self.has_groups():
            for i in range(self.get_data_length()):
                label = str(self.get_data()[i].keys()[0])
                key = self.get_data()[i][label].keys()[0]
                values.append(self.get_data()[i][label][key])
        else:
            for i in range(self.get_data_length()):
                key = self.get_data()[i].keys()[0]
                values.append(self.get_data()[i][key])

        return values

    def get_granularity(self):
        """
        Get granularity of statistics data.
        """
        return self.json['statistics']['granularity']
