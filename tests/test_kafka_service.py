import kafka
from mock import patch

from leexportpy.queryresponse import GroupByStatisticsResponse
from leexportpy.services.kafka_service import KafkaService
from tests.examples import request_examples as req_ex
from tests.examples import response_examples as resp_ex
from tests.examples import config_examples as conf_ex


def test_process_calls_push():
    with patch.object(KafkaService, "_push") as mocked_push:
        service_obj = KafkaService(resp_ex.FULL_GROUP_RESP, req_ex.SERVICE_API_KEY,
                                   conf_ex.KAFKA_SEARCH_CONFIG)
        service_obj.process()
        assert mocked_push.called


def test_transform():
    data = resp_ex.FULL_GROUP_RESP
    service_obj = KafkaService(data, req_ex.SERVICE_API_KEY, conf_ex.KAFKA_SEARCH_CONFIG)
    assert GroupByStatisticsResponse(data).get_values() == service_obj._transform()


@patch.object(kafka.KafkaProducer, '__init__')
@patch.object(kafka.KafkaProducer, 'flush')
@patch.object(kafka.KafkaProducer, 'close')
def test_push(mocked_close, mocked_flush, mocked_init):
    mocked_init.return_value = None
    data = resp_ex.FULL_GROUP_RESP
    service_obj = KafkaService(data, req_ex.SERVICE_API_KEY, conf_ex.KAFKA_SEARCH_CONFIG)
    service_obj._push(data)

    assert mocked_init.called
    assert mocked_flush.called
    assert mocked_close.called
