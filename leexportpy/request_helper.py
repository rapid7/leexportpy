import json
import logging
import time

import requests

logger = logging.getLogger(__name__)

QUERY_URL = 'https://rest.logentries.com/query/logs/'


def do_get_le_url(url, x_api_key, params=None):
    logger.debug("Making get request to the url: %s", url)
    header = {'x-api-key': x_api_key}
    return requests.get(url, headers=header, params=params)


def do_post_json_to_le(url, payload, x_api_key):
    logger.debug("Making post request with payload: %s to the url: %s", payload, url)
    header = {'x-api-key': x_api_key}
    return requests.post(url, json=payload, headers=header)


def get_continuity_final_response(response, auth):
    while True:
        logger.debug("Continuing getting response...")
        response = do_get_le_url(response.json()['links'][0]['href'], get_le_api_key(auth))
        if response.status_code != 200:
            logger.info("Response code is not 200, returning. Last response: %r", response)
            return None

        if 'links' not in response.json():
            logger.info("Got final response, returning.")
            return response
        else:
            logger.debug("links attribute found in a subsequent continue request. Should continue polling.")
            time.sleep(1)  # sleeping here to give lerest some time to finish querying.
            continue


def post_le_search(query_config, auth):
    logs = query_config.get('logs').split(":")
    to_ts = int(round(time.time() * 1000))
    from_ts = to_ts - int(query_config.get('query_range')) * 1000
    statement = query_config.get('statement')

    payload = {"logs": logs,
               "leql":
                   {"during": {"from": from_ts, "to": to_ts},
                    "statement": statement}
               }

    logger.info("Making request. Json: %s", json.dumps(payload))
    return do_post_json_to_le(QUERY_URL, payload, get_le_api_key(auth))


def get_le_api_key(auth):
    if auth.get('rw_api_key'):
        return auth.get('rw_api_key')
    else:
        return auth.get('ro_api_key')
