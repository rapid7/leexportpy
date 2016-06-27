class Service(object):
    def __init__(self, data, api_key, destination_config):
        self.data = data
        self.api_key = api_key
        self.destination_config = destination_config

    def process(self):
        raise NotImplementedError

    def transform(self):
        raise NotImplementedError

    def push(self, payload):
        return payload is not None
