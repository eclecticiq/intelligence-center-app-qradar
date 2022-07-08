"""Sighting Vars."""


SIGHTING_SCHEMA = {
    "data": {
        "data": {
            "confidence": "medium",
            "description": "test_desc",
            "type": "eclecticiq-sighting",
            "timestamp": "2022-03-10T05:37:42Z",
            "title": "title1",
            "security_control": {
                "type": "information-source",
                "identity": {
                    "name": "EclecticIQ Platform App for Qradar",
                    "type": "identity",
                },
                "time": {
                    "type": "time",
                    "start_time": "2022-03-10T05:37:42Z",
                    "start_time_precision": "second",
                },
            },
        },
        "meta": {"tags": ["Qradar Alert"], "ingest_time": "2022-03-10T05:37:42Z"},
    }
}
