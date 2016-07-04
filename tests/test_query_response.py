import pytest

from tests.examples import config_examples as conf_ex
from tests.examples import request_examples as req_ex
from tests.examples import response_examples as resp_ex
from leexportpy import queryresponse


def test_queryleql():
    leql = queryresponse.QueryLeql(req_ex.FROM_TIMESTAMP, req_ex.TO_TIMESTAMP, conf_ex.QUERY)
    assert "during" in leql.to_json()
    assert "statement" in leql.to_json()
    during = leql.during
    assert "from" in during
    assert "to" in during


def test_query_response():
    response = queryresponse.QueryResponse(resp_ex.FULL_TIMESERIES_RESP)
    assert response.is_events(response.data) is False
    assert response.is_statistics(response.data) is True


def test_statistics_response():
    response = queryresponse.StatisticsResponse(resp_ex.FULL_GROUP_RESP)

    expected_count = 1234
    expected_granularity = 120000
    expected_from_ts = 614563200000
    expected_to_ts = 1459296000000

    assert "leql" in response.to_json()
    assert "statistics" in response.to_json()
    assert response.get_count() == expected_count
    assert response.get_granularity() == expected_granularity
    assert response.get_from() == expected_from_ts
    assert response.get_to() == expected_to_ts
    assert response.is_timeseries(response.data) is False
    assert response.is_groupby(response.data) is True

    with pytest.raises(NotImplementedError):
        assert response.get_data_length()
    with pytest.raises(NotImplementedError):
        response.get_keys()
    with pytest.raises(NotImplementedError):
        response.get_values()


def test_statistics_response_with_timeseries():
    response = queryresponse.StatisticsResponse(resp_ex.FULL_TIMESERIES_RESP)
    assert response.is_timeseries(response.data) is True
    assert response.is_groupby(response.data) is False


def test_timeseries_response():
    ts_response = queryresponse.TimeSeriesStatisticsResponse(resp_ex.FULL_TIMESERIES_RESP)
    expected_data_length = 10
    expected_value = 2931
    expected_count = 27733.0
    expected_key = ts_response.convert_timestamp_to_str(614563200000)
    assert ts_response.get_timeseries() == resp_ex.TIMESERIES_STATISTICS['timeseries'][
        'global_timeseries']
    assert expected_value in ts_response.get_values()
    assert ts_response.get_data_length() == expected_data_length
    assert expected_key in ts_response.get_keys()
    assert ts_response.get_count() == expected_count


def test_group_response():
    group_response = queryresponse.GroupByStatisticsResponse(resp_ex.FULL_GROUP_RESP)
    expected_group_count = 4
    expected_value = 802.0
    expected_key = '200'
    assert group_response.get_data_length() == expected_group_count
    assert expected_value in group_response.get_values()
    assert expected_key in group_response.get_keys()
    assert group_response.get_groups() == resp_ex.GROUP_STATISTICS['groups']

