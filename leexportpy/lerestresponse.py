import datetime

DATEFORMAT = '%Y-%m-%dT%H:%M:%SZ'


# this class will be deprecated when LOG-7833 is resolved. queryresponse module will be put in to use with deprecation.
class LeRestResponse(object):
    def __init__(self, response_json):
        self.json = response_json

    def has_groups(self):  # migration to upcoming queryresponse is done
        return len(self.json['statistics'].get('groups')) != 0

    def get_logs(self):  # migration to upcoming queryresponse is done
        return self.json.get('logs')

    def get_leql(self):  # migration to upcoming queryresponse is done
        return self.json.get('leql')

    def get_data(self):  # migration to upcoming queryresponse is done
        if self.has_groups():
            return self.json['statistics'].get('groups')
        else:
            data_key = self.json['statistics']['timeseries'].keys()[0]
            return self.json['statistics']['timeseries'].get(data_key)

    def get_data_length(self):  # migration to upcoming queryresponse is done
        return len(self.get_data())

    def get_count(self):  # migration to upcoming queryresponse is done
        return self.json['statistics'].get('count')

    def get_keys(self):  # migration to upcoming queryresponse is done
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

    def get_values(self):  # migration to upcoming queryresponse is done
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

    def get_granularity(self):  # migration to upcoming queryresponse is done
        return self.json['statistics']['granularity']
