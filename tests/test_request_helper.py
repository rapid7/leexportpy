import httpretty
from mock import MagicMock, patch

import leexportpy.request_helper as helper
from examples import request_examples as req_ex


@httpretty.activate
def test_do_get_le_url():
    httpretty.register_uri(httpretty.GET, req_ex.DEST_URL,
                           body="OK")
    response = helper.do_get_le_url(req_ex.DEST_URL, req_ex.RO_API_KEY, {})

    assert response.text == "OK"


@httpretty.activate
def test_do_post_json_to_le():
    httpretty.register_uri(httpretty.POST, req_ex.DEST_URL,
                           body="OK")
    response = helper.do_post_json_to_le(req_ex.DEST_URL, req_ex.RO_API_KEY, {})

    assert response.text == "OK"


@patch('json.dumps')
@patch('leexportpy.request_helper.do_post_json_to_le')
def test_post_le_search(mocked_json_dumps, mocked_post_json):
    search = MagicMock()
    helper.post_le_search(search, {})
    assert mocked_json_dumps.called
    assert mocked_post_json.called


def test_get_le_api_key():
    ro_api_key = req_ex.RO_API_KEY
    rw_api_key = req_ex.RW_API_KEY
    auth = {'ro_api_key': ro_api_key}
    assert helper.get_le_api_key(auth) == ro_api_key

    auth['rw_api_key'] = rw_api_key
    assert helper.get_le_api_key(auth) == rw_api_key
