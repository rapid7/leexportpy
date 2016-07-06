import json
import logging
import time

import requests
import leexportpy

LOGGER = logging.getLogger(__name__)
QUERY_URL = 'https://rest.logentries.com/query/logs/'


def generate_headers(x_api_key):
    return {'x-api-key': x_api_key,
            'User-Agent': 'leexportpy %s' % leexportpy.__version__}


def do_get_le_url(url, x_api_key, params=None):
    """
    Make GET request to provided 'url' with provided x-api-key in the header and params if provided.

    :param url:         url to make get request
    :param x_api_key:   x-api-key for logentries
    :param params:      key value pairs to include in the get request.
    """
    LOGGER.debug("Making get request to the url: %s", url)
    headers = generate_headers(x_api_key)
    return requests.get(url, headers=headers, params=params)


def do_post_json_to_le(url, payload, x_api_key):
    """
    Make POST request to the provided 'url' with provided x-api-key in the header and payload.

    :param url:         endpoint url to make post request
    :param payload:     payload of the reuqest
    :param x_api_key:   x-api-key for Logentries
    """
    LOGGER.debug("Making post request with payload: %s to the url: %s", payload, url)
    headers = generate_headers(x_api_key)
    return requests.post(url, headers=headers, json=payload)


def get_continuity_final_response(response, auth):
    """
    Keep making get requests to the url provided in the response until there is no 'links'
    attribute in the response json.

    :param response:    first continuity response
    :param auth:        authentication configuration for Logentries
    """
    while True:
        LOGGER.debug("Continuing getting response...")
        response = do_get_le_url(response.json()['links'][0]['href'], get_le_api_key(auth))
        if response.status_code != 200:
            LOGGER.info("Response code is not 200, returning. Last response: %r", response)
            return None

        if 'links' not in response.json():
            LOGGER.info("Got final response, returning.")
            return response
        else:
            LOGGER.debug("links attribute found in a subsequent continue request. Should "
                         "continue polling.")
            time.sleep(1)  # sleeping here to give Logentries some time to finish the query.
            continue


def post_le_search(query_config, auth):
    """
    Prepare payload and post search to Logentries.

    :param query_config:    Search query config
    :param auth:            Authentication config for le
    """
    logs = query_config.get('logs').split(":")
    to_ts = int(round(time.time() * 1000))
    from_ts = to_ts - int(query_config.get('query_range')) * 1000
    statement = query_config.get('statement')

    payload = {"logs": logs,
               "leql": {"during": {"from": from_ts, "to": to_ts},
                        "statement": statement}}

    LOGGER.info("Making request. Json: %s", json.dumps(payload))
    return do_post_json_to_le(QUERY_URL, payload, get_le_api_key(auth))


def get_le_api_key(auth):
    """
    Get rw_api_key if provided in the configuration, otherwise get ro_api_key

    :param auth: authentication configuration for logentries
    """
    if auth.get('rw_api_key'):
        return auth.get('rw_api_key')
    else:
        return auth.get('ro_api_key')
