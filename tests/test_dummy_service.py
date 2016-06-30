import httpretty
from mock import patch

from tests.examples import request_examples as req_ex
from leexportpy.services.dummy_service import DummyService


def test_process_calls_push():
    with patch.object(DummyService, "push") as mocked_push:
        service_obj = DummyService("data_to_push", req_ex.SERVICE_API_KEY, {})
        service_obj.process()
        assert mocked_push.called


def test_transform():
    data = "data_to_push"
    service_obj = DummyService(data, req_ex.SERVICE_API_KEY, {})
    assert data == service_obj.transform()["payload"]


@httpretty.activate
def test_push():
    data = "data_to_push"
    service_obj = DummyService(data, req_ex.SERVICE_API_KEY, {"push_url": req_ex.DEST_URL})
    httpretty.register_uri(httpretty.PUT, req_ex.DEST_URL)
    service_obj.push(data)

    assert httpretty.has_request()
    assert httpretty.last_request().body == data
