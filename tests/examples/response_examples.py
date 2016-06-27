LEQL = {
    "during": {
        "from": 1234,
        "to": 1235
    },
    "statement": "where(event)"
}

LOGS = [
    "log_key_123"
]
GROUP_STATISTICS = {
    "from": 614563200000,
    "to": 1459296000000,
    "count": 1234,
    "groups": [{
        "200": {
            "count": 802.0,
            "min": 802.0,
            "max": 802.0,
            "sum": 802.0,
            "bytes": 802.0,
            "percentile": 802.0,
            "unique": 802.0,
            "average": 802.0
        }
    }, {
        "400": {
            "count": 839.0,
            "min": 839.0,
            "max": 839.0,
            "sum": 839.0,
            "bytes": 839.0,
            "percentile": 839.0,
            "unique": 839.0,
            "average": 839.0
        }
    }, {
        "404": {
            "count": 839.0,
            "min": 839.0,
            "max": 839.0,
            "sum": 839.0,
            "bytes": 839.0,
            "percentile": 839.0,
            "unique": 839.0,
            "average": 839.0
        }
    }, {
        "status": {
            "count": 205.0,
            "min": 205.0,
            "max": 205.0,
            "sum": 205.0,
            "bytes": 205.0,
            "percentile": 205.0,
            "unique": 205.0,
            "average": 205.0
        }
    }],
    "stats": {},
    "granularity": 120000
}
TIMESERIES_STATISTICS = {
    "from": 614563200000,
    "to": 1459296000000,
    "count": 1234,
    "stats": {
        "global_timeseries":
            {"count": 27733.0}
    },
    "granularity": 120000,
    "timeseries": {
        "global_timeseries": [
            {"count": 2931.0},
            {"count": 2869.0},
            {"count": 2852.0},
            {"count": 2946.0},
            {"count": 2733.0},
            {"count": 2564.0},
            {"count": 2801.0},
            {"count": 2773.0},
            {"count": 2698.0},
            {"count": 2566.0}
        ]
    }
}
FULL_GROUP_RESP = {"logs": LOGS, "statistics": GROUP_STATISTICS, "leql": LEQL}
FULL_TIMESERIES_RESP = {"logs": LOGS, "statistics": TIMESERIES_STATISTICS, "leql": LEQL}
