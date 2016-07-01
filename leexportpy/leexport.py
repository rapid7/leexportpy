import argparse
import logging
import os
import pkgutil
import signal
import sys
import threading
from pydoc import locate

from configobj import ConfigObj
from daemonize import Daemonize
from twisted.internet import reactor
from twisted.internet import task

from leexportpy import services
from leexportpy.search import Search

CONFIG = None
SERVICE_CLASS_MAPPER = {}
SEARCH_TASKS = []

PID_FILE_PATH = '/var/run/leexportpy.pid'
LOG_FILE_PATH = '/var/log/leexportpy.log'
PRINT_THREAD_INFO_INTERVAL_SECONDS = 100
CONFIG_LOAD_INTERVAL_SECONDS = 300
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(threadName)s - %(message)s"
LOGGING_LEVEL = logging.INFO


def configure_options():
    """Configure cli argument configs"""

    parser = argparse.ArgumentParser(prog='leexportpy',
                                     description='Leexportpy by Logentries by Rapid7')
    subparsers = parser.add_subparsers(help='subcommands')
    start_parser = subparsers.add_parser(name='start', help='this command group is used while '
                                                            'starting the app')
    start_parser.add_argument('-c', '--config-file', help='Config file path.', required=True)
    start_parser.add_argument('-d', '--daemonize', help='Daemonize the process or not',
                              required=False, default=False,
                              action='store_true')
    subparsers.add_parser(name='stop', help='this command is used while stopping the daemon')

    return parser.parse_args()


CLI_ARGS = configure_options()


def discover_services():
    """
    Discover services placed in 'services' directory.
    """

    discovered_services = {}
    for importer, modname, ispkg in pkgutil.iter_modules(services.__path__):
        if modname.endswith('_service'):
            name_arr = str.split(modname, '_')
            service_name = modname.replace('_service', '')
            class_name = ''
            for word in name_arr:
                class_name += str.capitalize(word)
            discovered_services[service_name] = {'module': modname, 'class': class_name}
        else:
            logging.warn("Extraneous file found in the services directory while discovering "
                         "services: %s", modname)

    logging.info("Discovered services after analyzing files in services directory: %s" + str(
        discovered_services))
    import_and_load_services(discovered_services)


def import_and_load_services(discovered_services):
    """
    Do the importing and loading of service classes into memory.

    """
    for service_name, data in discovered_services.items():
        class_fqn = 'leexportpy.services.' + data['module'] + '.' + data['class']
        logging.info("Class fqn: %s", class_fqn)
        service_class = locate(class_fqn)
        SERVICE_CLASS_MAPPER[service_name] = service_class

    logging.info("Discovered & reflected service map: " + str(SERVICE_CLASS_MAPPER))


def do_every(interval, job, params=None):
    """
    Do this 'job' every 'interval' provided. If 'params' is provided, run it with 'params'.

    :param interval: interval to run the job
    :param job: the job to be run
    :param params: optional params for the job
    :return:
    """

    logging.info("Scheduling job: %r, params: %r", job, params)
    if params:
        looping_task = task.LoopingCall(job, params)
        SEARCH_TASKS.append(looping_task)
    else:
        looping_task = task.LoopingCall(job)

    looping_task.start(interval)


def do_search_concurrently(search):
    """
    Run the search task concurrently, in another thread of the threadpool.

    :param search: search task to be run concurrently
    """
    logging.debug("Scheduling search to run concurrently.")
    reactor.callInThread(search.start)
    SEARCH_TASKS.append(search)


def print_thread_info():
    """
    Print thread count and some useful information.

    """
    logging.debug("Active thread count %i", threading.activeCount())
    logging.debug("Active threads: %r", threading.enumerate())


def start_leexportpy_jobs():
    """
    Start main jobs. Configure logging. Run twisted reactor.
    """

    if CLI_ARGS.daemonize is True:  # we are configuring logging here to include it in the
                                    # daemon context.
        logging.basicConfig(filename=LOG_FILE_PATH, level=LOGGING_LEVEL, format=LOG_FORMAT)
    else:
        logging.basicConfig(stream=sys.stdout, level=LOGGING_LEVEL, format=LOG_FORMAT)

    discover_services()

    do_every(PRINT_THREAD_INFO_INTERVAL_SECONDS, print_thread_info)
    do_every(CONFIG_LOAD_INTERVAL_SECONDS, load_config_start_searches)
    reactor.run()


def start_search_tasks():
    """
    Before everything, kill if there is any running search tasks. Then start the search tasks
    concurrently.

    """
    global SEARCH_TASKS
    logging.info("(Re)populated config collections from config file. "
                 "Cancelling previous loops and restarting them again with the new config.")

    for looping_task in SEARCH_TASKS:
        logging.info("Cancelling this loop: %r", looping_task)
        looping_task.stop()
    SEARCH_TASKS = []

    searches = CONFIG['Searches'].values()
    search_count = len(searches)
    logging.info("Search count: %d", search_count)
    reactor.suggestThreadPoolSize(search_count)
    try:
        for search in searches:
            search_obj = Search(SERVICE_CLASS_MAPPER.get(search['destination']['service']), search,
                                CONFIG)
            do_search_concurrently(search_obj)
    except Exception as exception:
        logging.exception("Exception occurred while processing search. %s", exception.message)


def load_config_start_searches():
    """
    Load config from config file provided in cli_args and start search tasks.

    """
    global CONFIG
    config_file_path = CLI_ARGS.config_file
    logging.info("Config file path: %s", CLI_ARGS.config_file)
    if config_file_path:
        CONFIG = ConfigObj(config_file_path, file_error=True, raise_errors=True)
        logging.info("Updated config file content: %s", CONFIG)
        start_search_tasks()
    else:
        logging.error("This should not happen.")


def main():
    """
    Running or stopping business logic implemented here.
    Start means, start the process either in background or foreground.
    Stop means, stop the daemon.

    """
    if 'start' in sys.argv:
        print "Trying to run the app..."

        if CLI_ARGS.daemonize is True:
            if os.path.isfile(PID_FILE_PATH) is not True:
                print "Trying to run in daemonized mode. Check log file for further insight: " \
                      "%s", LOG_FILE_PATH
                daemon = setup_daemon()
                daemon.start()
            else:
                print "Tried to run the app but an existing pid file found. " \
                      "Looks like it was not shutdown gracefully last time." \
                      "file: " + PID_FILE_PATH
        else:
            print "Running in foreground, CTRL+C to exit the process."
            start_leexportpy_jobs()

    elif 'stop' in sys.argv:
        try:
            print "Trying to terminate the daemon..."
            terminate()
        except IOError as exception:
            if exception.errno == 2:  # meaning pid file not found and so there is no running
                # instance
                print "No leexportpy instance found so it could not be stopped."
            elif exception.errno == 3:
                print "Pid file found but no such process was found. Please remove the pid file " \
                      "at: " + PID_FILE_PATH
            else:
                print "An unexpected error occurred while stopping leexportpy: ", exception
                logging.exception("An unexpected error occurred while stopping leexportpy")
    else:
        print "This should not happen."


def setup_daemon():
    """
    Setup the daemon. Set the PID_FILE, action, logger config.

    """
    return Daemonize(app='leexportpy', pid=PID_FILE_PATH, action=start_leexportpy_jobs,
                     logger=logging.getLogger("leexportpy_daemon"))


def terminate():
    """
    Terminate the daemon.

    """
    # this function is called when we need to stop the "daemon"
    pid = int(open(PID_FILE_PATH, 'r').read())
    os.kill(pid, signal.SIGTERM)
    print "Daemon terminated."


if __name__ == '__main__':
    main()
