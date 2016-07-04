import logging

from kafka import KafkaProducer

from leexportpy.queryresponse import GroupByStatisticsResponse, QueryResponse, StatisticsResponse, \
    TimeSeriesStatisticsResponse
from leexportpy.service import Service

LOGGER = logging.getLogger(__name__)


class KafkaService(Service):
    """
    An example kafka service to produce transformed Logentries REST statistics values to a specific
    kafka topic.

    We are sending statistics "values" to a specific kafka topic here. We can
    """

    def __init__(self, response, api_key, destination_config):
        """
        Initialize KafkaService.
        """
        super(KafkaService, self).__init__(response, api_key, destination_config)

    def process(self):
        """
        Process this KafkaService call.
        """
        self._push(self._transform())

    def _transform(self):
        """
        Transform payload.
        """
        if QueryResponse.is_statistics(self.response):
            if StatisticsResponse.is_groupby(self.response):
                return GroupByStatisticsResponse(self.response).get_values()
            else:
                return TimeSeriesStatisticsResponse(self.response).get_values()

    def _push(self, payload):
        if super(KafkaService, self)._push(payload):
            LOGGER.info("Pushing payload to kafka: %s", str(payload))
            brokers = self.destination_config['brokers'].split(',')
            topic = self.destination_config['topic']
            kafka_producer = KafkaProducer(bootstrap_servers=brokers)
            for values in payload:
                kafka_producer.send(topic, str(values).encode('utf-8'))
            kafka_producer.flush(3)
            kafka_producer.close(3)
        else:
            LOGGER.warn("Payload is none, nothing to push.")
