import examples.response_examples as resp_ex
from leexportpy.lerestresponse import LeRestResponse

EXPECTED_COUNT = 1234
EXPECTED_GROUP_COUNT = 4
EXPECTED_TS_COUNT = 10
EXPECTED_GRANULARITY = 120000
EXPECTED_LOG_KEY_COUNT = 1


def test_get_granularity():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert group_obj.get_granularity() == EXPECTED_GRANULARITY
    assert ts_obj.get_granularity() == EXPECTED_GRANULARITY


def test_get_values():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert len(group_obj.get_values()) == EXPECTED_GROUP_COUNT
    assert len(ts_obj.get_values()) == EXPECTED_TS_COUNT


def test_get_keys():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert len(group_obj.get_keys()) == EXPECTED_GROUP_COUNT
    assert len(ts_obj.get_keys()) == EXPECTED_TS_COUNT


def test_get_count():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert group_obj.get_count() == EXPECTED_COUNT
    assert ts_obj.get_count() == EXPECTED_COUNT


def test_get_data_length():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert group_obj.get_data_length() == EXPECTED_GROUP_COUNT
    assert ts_obj.get_data_length() == EXPECTED_TS_COUNT


def test_get_data():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert len(group_obj.get_data()) == EXPECTED_GROUP_COUNT
    assert len(ts_obj.get_data()) == EXPECTED_TS_COUNT


def test_get_leql():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert group_obj.get_leql() == resp_ex.LEQL
    assert ts_obj.get_leql() == resp_ex.LEQL


def test_get_logs():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert len(group_obj.get_logs()) == EXPECTED_LOG_KEY_COUNT
    assert len(ts_obj.get_logs()) == EXPECTED_LOG_KEY_COUNT


def test_has_groups():
    group_obj = LeRestResponse(resp_ex.FULL_GROUP_RESP)
    ts_obj = LeRestResponse(resp_ex.FULL_TIMESERIES_RESP)

    assert group_obj.has_groups() is True
    assert ts_obj.has_groups() is False
