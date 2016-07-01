import httpretty
from mock import patch

from tests.examples import config_examples as conf_ex
from tests.examples import request_examples as req_ex
from tests.examples import response_examples as resp_ex
from leexportpy.services.geckoboard_service import GeckoboardService


def test_number_stat_process_calls_push():
    with patch.object(GeckoboardService, 'push') as mocked_number_stat_push:
        gecko_job_number_stat = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                                  req_ex.SERVICE_API_KEY,
                                                  conf_ex.GECKO_NUMBER_STAT_CONFIG)
        gecko_job_number_stat.process()
        assert mocked_number_stat_push.called


def test_line_chart_process_calls_push():
    with patch.object(GeckoboardService, 'push') as mocked_line_chart_push:
        gecko_job_line_chart = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                                 req_ex.SERVICE_API_KEY,
                                                 conf_ex.GECKO_LINE_CHART_CONFIG)
        gecko_job_line_chart.process()
        assert mocked_line_chart_push.called


def test_pie_chart_process_calls_push():
    with patch.object(GeckoboardService, 'push') as mocked_pie_chart_push:
        gecko_job_pie_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                                req_ex.SERVICE_API_KEY,
                                                conf_ex.GECKO_PIE_CHART_CONFIG)
        gecko_job_pie_chart.process()
        assert mocked_pie_chart_push.called


def test_bar_chart_process_calls_push():
    with patch.object(GeckoboardService, 'push') as mocked_bar_chart_push:
        gecko_job_bar_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                                req_ex.SERVICE_API_KEY,
                                                conf_ex.GECKO_BAR_CHART_CONFIG)
        gecko_job_bar_chart.process()
        assert mocked_bar_chart_push.called


@httpretty.activate
def test__number_stat_push():
    httpretty.register_uri(httpretty.POST, req_ex.DEST_URL,
                           body="OK")
    gecko_job_number_stat = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                              req_ex.SERVICE_API_KEY,
                                              conf_ex.GECKO_NUMBER_STAT_CONFIG)
    gecko_job_number_stat.push({})

    assert httpretty.has_request()


@httpretty.activate
def test_line_chart_push():
    httpretty.register_uri(httpretty.POST, req_ex.DEST_URL,
                           body="OK")
    gecko_job_line_chart = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                             req_ex.SERVICE_API_KEY,
                                             conf_ex.GECKO_LINE_CHART_CONFIG)
    gecko_job_line_chart.push({})

    assert httpretty.has_request()


@httpretty.activate
def test_pie_chart_push():
    httpretty.register_uri(httpretty.POST, req_ex.DEST_URL,
                           body="OK")
    gecko_job_pie_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                            req_ex.SERVICE_API_KEY,
                                            conf_ex.GECKO_PIE_CHART_CONFIG)
    gecko_job_pie_chart.push({})

    assert httpretty.has_request()


@httpretty.activate
def test_bar_chart_push():
    httpretty.register_uri(httpretty.POST, req_ex.DEST_URL,
                           body="OK")
    gecko_job_bar_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                            req_ex.SERVICE_API_KEY,
                                            conf_ex.GECKO_BAR_CHART_CONFIG)
    gecko_job_bar_chart.push({})

    assert httpretty.has_request()


def test_format_number_stat_data():
    gecko_job_number_stat = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                              req_ex.SERVICE_API_KEY,
                                              conf_ex.GECKO_NUMBER_STAT_CONFIG)
    number_stat = gecko_job_number_stat.format_number_stat_data()

    assert "data" in number_stat
    number_stat_data = number_stat.get("data")
    assert "item" in number_stat_data
    item = number_stat_data["item"]
    assert item[0]

    the_item = item[0]
    assert "value" in the_item
    assert the_item["value"] == 27733.0
    assert "text" in the_item
    assert the_item["text"] == "number_stat_text"


def test_format_bar_chart_data():
    gecko_job_bar_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                            req_ex.SERVICE_API_KEY,
                                            conf_ex.GECKO_BAR_CHART_CONFIG)
    bar_chart_json = gecko_job_bar_chart.format_bar_chart_data()

    assert "data" in bar_chart_json
    bar_chart_data = bar_chart_json.get("data")
    assert "x_axis" in bar_chart_data
    assert "y_axis" in bar_chart_data
    assert "series" in bar_chart_data


def test_format_pie_chart_data():
    gecko_job_pie_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                            req_ex.SERVICE_API_KEY,
                                            conf_ex.GECKO_PIE_CHART_CONFIG)
    pie_data = gecko_job_pie_chart.format_pie_chart_data()

    assert "data" in pie_data

    item_data = pie_data["data"]
    assert "item" in item_data
    assert len(resp_ex.GROUP_STATISTICS.get('groups')) == len(pie_data['data']['item'])


def test_format_line_chart_data():
    gecko_job_line_chart = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                             req_ex.SERVICE_API_KEY,
                                             conf_ex.GECKO_LINE_CHART_CONFIG)
    line_chart_data = gecko_job_line_chart.format_line_chart_data()

    assert "data" in line_chart_data
    assert line_chart_data["data"]["series"][0]["name"] == conf_ex.GECKO_LINE_CHART_CONFIG["name"]


def test_line_chart_transform():
    with patch.object(GeckoboardService, 'transform', return_value=None) as mock_transform:
        gecko_job_line_chart = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                                 req_ex.SERVICE_API_KEY,
                                                 conf_ex.GECKO_LINE_CHART_CONFIG)
        gecko_job_line_chart.transform()
        assert mock_transform.called


def test_pie_chart_transform():
    with patch.object(GeckoboardService, 'transform', return_value=None) as mock_transform:
        gecko_job_pie_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                                req_ex.SERVICE_API_KEY,
                                                conf_ex.GECKO_PIE_CHART_CONFIG)
        gecko_job_pie_chart.transform()
        assert mock_transform.called


def test_number_stat_transform():
    with patch.object(GeckoboardService, 'transform', return_value=None) as mock_transform:
        gecko_job_number_stat = GeckoboardService(resp_ex.FULL_TIMESERIES_RESP,
                                                  req_ex.SERVICE_API_KEY,
                                                  conf_ex.GECKO_NUMBER_STAT_CONFIG)
        gecko_job_number_stat.transform()
        assert mock_transform.called


def test_bar_chart_transform():
    with patch.object(GeckoboardService, 'transform', return_value=None) as mock_transform:
        gecko_job_bar_chart = GeckoboardService(resp_ex.FULL_GROUP_RESP,
                                                req_ex.SERVICE_API_KEY,
                                                conf_ex.GECKO_BAR_CHART_CONFIG)
        gecko_job_bar_chart.transform()
        assert mock_transform.called
