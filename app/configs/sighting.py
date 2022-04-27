"""Sighting Vars."""
SIGHTING_VALUES = {
    "eiq_sighting_s_ip": {"action_type": "ipv4", "param_value": "sourceip"},
    "eiq_sighting_d_ip": {"action_type": "ipv4", "param_value": "destinationip"},
    "eiq_sighting_hash_md5": {"action_type": "md5", "param_value": "File Hash"},
    "eiq_sighting_email": {"action_type": "email", "param_value": "email"},
    "eiq_sighting_domain": {"action_type": "domain", "param_value": "domain"},
    "eiq_sighting_uri": {"action_type": "uri", "param_value": "URL"},
}

SIGHTINGS_FIELDS_LIST = [
    "eiq_sighting_s_ip",
    "eiq_sighting_d_ip",
    "eiq_sighting_hash_md5",
    "eiq_sighting_email",
    "eiq_sighting_domain",
    "eiq_sighting_uri",
]


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
