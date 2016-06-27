import json

import httpretty
import requests
from mock import patch
from twisted.internet import task

from examples import config_examples as conf_ex
from examples import request_examples as req_ex
from leexportpy.search import Search
from leexportpy.services.dummy_service import DummyService


def test_start():
    with patch.object(task.LoopingCall, 'start') as mocked_start:
        search = Search(DummyService, conf_ex.DUMMY_SEARCH_CONFIG, conf_ex.DUMMY_CONFIG)
        search.start()
        assert mocked_start.called


def test_stop():
    with patch.object(task.LoopingCall, 'stop') as mocked_stop:
        search = Search(DummyService, conf_ex.DUMMY_SEARCH_CONFIG, conf_ex.DUMMY_CONFIG)
        search.start()
        search.stop()
        assert mocked_stop.called


@patch('leexportpy.request_helper.post_le_search')
def test_query_and_push_task(mocked_post_le_search):
    with patch.object(Search, 'handle_response') as mocked_handle_response:
        search = Search(DummyService, conf_ex.DUMMY_SEARCH_CONFIG, conf_ex.DUMMY_CONFIG)
        search.query_and_push_task()
        assert mocked_post_le_search.called
        assert mocked_handle_response.called


@httpretty.activate
@patch('leexportpy.request_helper.get_continuity_final_response')
def test_handle_cont_response(mocked_cont_final_resp):
    with patch.object(Search, 'process_final_response') as mocked_process_final_resp:
        search = Search(DummyService, conf_ex.DUMMY_SEARCH_CONFIG, conf_ex.DUMMY_CONFIG)
        httpretty.register_uri(httpretty.GET, req_ex.DEST_URL,
                               body={},
                               status=202)
        continuity_response = requests.get(req_ex.DEST_URL)
        search.handle_response(continuity_response)
        assert mocked_process_final_resp.called


@httpretty.activate
@patch('leexportpy.request_helper.get_continuity_final_response')
def test_handle_ok_response(mocked_cont_final_resp):
    with patch.object(Search, 'process_final_response') as mocked_process_final_resp:
        search = Search(DummyService, conf_ex.DUMMY_SEARCH_CONFIG, conf_ex.DUMMY_CONFIG)
        httpretty.register_uri(httpretty.GET, req_ex.DEST_URL,
                               body=json.dumps({}),
                               status=200,
                               content_type='application/json')
        ok_response = requests.get(req_ex.DEST_URL)
        search.handle_response(ok_response)
        assert mocked_process_final_resp.called


@httpretty.activate
def test_process_final_response():
    with patch.object(DummyService, 'process') as mocked_process_method:
        search = Search(DummyService, conf_ex.DUMMY_SEARCH_CONFIG, conf_ex.DUMMY_CONFIG)
        httpretty.register_uri(httpretty.GET, req_ex.DEST_URL,
                               body=json.dumps({}),
                               status=200,
                               content_type='application/json')
        final_response = requests.get(req_ex.DEST_URL)
        search.process_final_response(final_response)
        assert mocked_process_method.called
