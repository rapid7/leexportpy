leexportpy
==========

Introduction
------------

Leexportpy is an application which transforms and pushes Logentries statistics data from Logentries to 3rd party applications. After getting the instructions from `config.ini` file which can include multiple exports with query and destination configs, leexportpy runs every export concurrently to meet configured needs.

If you want to use supported 3rd parties only, all you need to do is fill the config file and run the app!

If your desired 3rd party is not on the supported list, following the [rules for creating a new service](#adding-a-new-service) and adding a new service support to the app is as easy as pie! You are more than welcome if you want to contribute to the project with your 3rd party service modules.

Supported 3rd parties
---------------------

### Geckoboard      `geckoboard_service.py`

Custom search destination configs:
        
    widget_type = "Geckoboard widget type where letters are all lowercase and spaces replaced by underscores (_)" E.g: "line_chart"

##### [Line Chart](https://developer.geckoboard.com/#line-chart)

    widget_type = line_chart
    name = "Name of the series to be drawn"

##### [Bar Chart](https://developer.geckoboard.com/#bar-chart)

    widget_type = bar_chart

##### [Pie Chart](https://developer.geckoboard.com/#pie-chart)

    widget_type = pie_chart
    
##### [Number Stat](https://developer.geckoboard.com/#number-and-secondary-stat)
        
    widget_type = number_stat
    text = "Text to show at Number Stat widget"

### Hosted Graphite `hosted_graphite_service.py`
    
    metric_name = "hosted graphite metric name"

### Kafka           `kafka_service.py`
This is an attempt to show how to append your transformed Logentries data to a Kafka topic. Consumers of this topic can decide what action they are going to take based on the data produced into the queue.

Leexportpy expects a statistics query here and gets the count values in the response for each group or timestamp data and then appends to the provided Kafka topic.

    brokers = <comma separated host:port of brokers e.g: “localhost:9092,localhost:9093”> 
    topic   = <kafka topic to append data>

### Dummy           `dummy_service.py`
This service module is an example to show how to create a new service module. Simply, `transform()` method returns data directly without any manipulation and `push()` method logs some info in the logger.

Deployment
----------

Leexportpy is completely installable via pip:

`pip install leexportpy`

or

`pip install <url to repository>`

or

`pip install <directory to local copy of the project>`

After a successful install, you will be able to manage the app with `leexportpy start` or `leexportpy stop` commands. See [Running](#running) for details.

Running
-------

### Starting

    usage: leexportpy start [-h] -c CONFIG_FILE [-d]
    
    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG_FILE, --config-file CONFIG_FILE
                            Config file path.
      -d, --daemonize       Daemonize the process or not

    Example: sudo application start -c /etc/leexportpy/config.ini -d

There are two types of running modes are available:

In the background(as a daemon):

In daemon mode, the user managing leexportpy should have sudo privileges because of pid file location and log file location.

`sudo application start -c /etc/leexportpy/config.ini -d`

In the foreground:

`application start -c /etc/leexportpy/config.ini`

**Note:** if it is going to be run in daemonized mode, config file path should be absolute path of the file.

### Stopping

If running in the background as a daemon(with -d argument):

    sudo application stop

**Note** stop command is applicable for daemonized mode only.

Configuration file
------------------
Configuration file should be given to the leexportpy as an argument along with start command and a mandatory option of `-c` or `--config-file` with the absolute path of file config file. For example: `sudo leexportpy.py start -c /etc/leexportpy/config.ini -d

    [LE]
        x_api_key = {your logentries read-only or read/write api key}
    
    [Services]
        [[{your 3rd party service name}]]
            api_key = {your api key for the 3rd party service}
    
        [[{another service names}]]
            api_key = {another api key}
    
    [Searches]
        [[Search0]] # search section names should be unique, other than that they don't affect the functionality.
            [[[query]]]
                logs = {le log-key to query}
                query_period = {querying interval in secodns}
                statement = {your leql query}
                query_range = {your timerange from now() in seconds}
            [[[destination]]]
                push_url = {your 3rd party url to push transformed data}
                service = {your service name - must match with the one in the Services section}
                custom_key0 = {custom_value0}
                custom_keyn = {custom_valuen}

        [[SearchN]] # search section names should be unique, other than that they don't affect the functionality.
            [[[query]]]
                ...
            [[[destination]]]
                ...

Adding a new service
--------------------

As leexportpy automatically discovers available 3rd party services at runtime, some rules should be followed by developers.

### Module Location
All service modules should be placed under `services` package directory.

### Module Name
Module name should always end with `_service.py`. The prefix should be the name of the service, spaces replaced by underscores (`_`) and all letters must be lowercased. Example: module name for the service `My Application` should be: `my_application_service.py`

### Class Name
Class name should be the capitalized version of the module name, underscores (`_`) replaced with empty string. Example: class name for `my_application_service.py` should be: `MyApplicationService`

### Methods to implement
`process()` method should call `_push` with the payload created by `_transform()`. This is the module that triggers transforming and pushing.
`_transform()` method should be used to transform the data returned by Logentries REST API to the format expected by 3rd party.
`_push(url, api_key, payload)` method gets a url to push transformed data, an `api key` and a payload returned by transform() method which is your data to be pushed to the provided url. This method should be doing the necessary HTTP request such as POST/GET/PUT etc.

### Config file service name for searches
The `service` provided in every search in `config.ini` should be your module name without the `_service.py` or in other words, your service name with only lowercase letters and spaces replaced by underscores. Example: service name: `My Application`, module name: `my_application_service.py` and service key in config ini: `my_application`
