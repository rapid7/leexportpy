import json
import logging

from twisted.internet import task

from leexportpy import request_helper

LOGGER = logging.getLogger(__name__)


class Search(object):
    """
    Class that handles search and push algorithms for exports.
    """

    def __init__(self, service_class, search_config, config):

        """
        Initialize this Search object with the related search_config.

        :param search_config: search config from config file.
        """
        self.service_class = service_class
        self.search_config = search_config
        self.config = config
        self.query_period = int(search_config['query'].get('query_period'))
        self.looping_call = None

    def process_final_response(self, resp):
        """
        Structure the response object, hand it to related service class.

        :param resp: the final response object.
        """
        LOGGER.debug("Receieved final response: %s", resp.json())
        destination_config = self.search_config.get('destination')
        service_name = destination_config.get('service')
        service_api_key = self.config['Services'][service_name].get('api_key')

        if self.service_class:
            LOGGER.info("A discovered service! "
                        "Service name: %s, class: %r", service_name, self.service_class)
            service_object = self.service_class(resp.json(), service_api_key,
                                                destination_config)
            service_object.process()
        else:
            LOGGER.error(
                'Unknown transformation type: %s, Are you sure the service class is '
                'appropriately placed in the "services" directory?', service_name)
            return

    def handle_response(self, response):
        """
        Get the response, check status codes and decide what to do accordingly.

        :param response: response to be handled
        """
        LOGGER.debug("Response status code: %i", response.status_code)

        if response.status_code >= 500:
            LOGGER.warning(
                "Logentries endpoint returned unexpected error code %i, search task will be "
                "executed again in the next interval",
                response.status_code)
            return

        if response.status_code >= 400:
            LOGGER.error(
                "Logentries REST endpoint returned error code: %i, "
                "please check if there is something wrong with your search config: %s."
                "Now stopping this search to avoid further malformed executions until config "
                "file is reloaded.",
                response.status_code, self.search_config)
            self.stop()
            return

        if response.status_code == 201:
            LOGGER.warning("I have got a 201 response status code but I should have not.")
            return

        # after the first continuity response, if the query is still running on the server side,
        # server will return 200 with 'links' inside the json response for the following requests
        if response.status_code == 202:
            final_response = request_helper.get_continuity_final_response(response,
                                                                          self.config['LE'])
            if final_response is None:
                # a non-200 continuity response after the first 202 will produce an Empty
                # response and needs no more work

                return

            self.process_final_response(final_response)

        if response.status_code == 200:
            # this is where we get into transforming & pushing business
            LOGGER.debug("Response content: %s", json.dumps(response.json()))
            self.process_final_response(response)

    def query_and_push_task(self):
        """
        Query and push task for the Search.

        :return:
        """
        LOGGER.debug("Query period for search (seconds): %i", self.query_period)

        auth = self.config['LE']

        self.handle_response(request_helper.post_le_search(self.search_config.get('query'), auth))
        LOGGER.info("Waiting for the next cycle of query period. see you in %s seconds.",
                    self.query_period)

    def start(self):
        """
        Start this periodic search job.
        """
        LOGGER.info("Job starting: %s", self.search_config)
        self.looping_call = task.LoopingCall(self.query_and_push_task)
        self.looping_call.start(self.query_period, True)

    def stop(self):
        """
        Stop this periodic search job if it is running.
        """
        if self.looping_call and self.looping_call.running:
            self.looping_call.stop()
            LOGGER.info("Stopped running search: %s", self.search_config)
        else:
            LOGGER.warn("This looping task was not started but tried to be stopped.")
