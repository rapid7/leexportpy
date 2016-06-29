from tests.examples import request_examples

GECKO_NUMBER_STAT_CONFIG = {"text": "number_stat_text",
                            "widget_type": "number_stat",
                            "push_url": request_examples.DEST_URL}
GECKO_LINE_CHART_CONFIG = {"name": "line_chart_test",
                           "widget_type": "line_chart",
                           "push_url": request_examples.DEST_URL}
GECKO_PIE_CHART_CONFIG = {"widget_type": "pie_chart",
                          "push_url": request_examples.DEST_URL}
GECKO_BAR_CHART_CONFIG = {"widget_type": "bar_chart",
                          "push_url": request_examples.DEST_URL}
SEARCH_HOSTED_GRAPHITE = {"metric_name": "hg_metric",
                          "push_url": request_examples.DEST_URL}
QUERY = 'where(event) calculate(count)'
DUMMY_SEARCH_CONFIG = {'query': {'query_period': 300, 'logs': '', 'query_range': 30000, 'statement': QUERY},
                       'destination': {'service': 'dummy'}}
DUMMY_CONFIG = {'LE': {'rw_api_key': 'test_rw_api_key', 'ro_api_key': 'test_ro_api_key'},
                'Services':
                    {'dummy': {'api_key': 'my_dummy_api_key'}}}
