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


def test_queryresponse():
    response = queryresponse.QueryResponse(resp_ex.LOGS, resp_ex.LEQL,
                                           resp_ex.GROUP_STATISTICS)

    expected_count = 1234
    assert "leql" in response.to_json()
    assert "logs" in response.to_json()
    assert "statistics" in response.to_json()
    assert response.get_count() == expected_count
    with pytest.raises(NotImplementedError):
        response.get_keys()
    with pytest.raises(NotImplementedError):
        response.get_values()


def test_timeseriesresponse():
    ts_response = queryresponse.TimeseriesQueryResponse(resp_ex.LOGS, resp_ex.LEQL,
                                                        resp_ex.TIMESERIES_STATISTICS)
    expected_data_length = 10
    assert ts_response.get_values() is not None
    assert ts_response.get_data_length() == expected_data_length
    assert ts_response.get_keys() is not None


def test_groupresponse():
    group_response = queryresponse.GroupbyQueryResponse(resp_ex.LOGS, resp_ex.LEQL,
                                                        resp_ex.GROUP_STATISTICS)
    expected_group_count = 4
    assert group_response.get_data_length() == expected_group_count
    assert group_response.get_values() is not None
    assert group_response.get_keys() is not None
