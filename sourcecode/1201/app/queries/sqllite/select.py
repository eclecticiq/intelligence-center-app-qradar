"""Select Queries."""


SELECT_TABLE_QUERIES = {
    # Search sighting count
    "SEARCH_SIGHTING_COUNT_BY_TIME": """select count(id) as count, strftime(\"%d-%m-%Y\",datetime(time, 'unixepoch')) as day
     from eiq_sighting where confidence in {} and type in {} and time>={} and time<={}
     group by day;""",
    "SEARCH_SIGHTING_COUNT_BY_CONFIDENCE": """select count(id) as count, confidence
    from eiq_sighting where confidence in {} and type in {} and time>={} and time<={}
    group by confidence;""",
    "SEARCH_SIGHTING_COUNT_BY_OBSERVABLE_TYPE": """select count(id) as count, type
    from (select * from eiq_sighting where confidence in {} and type in {} and time>={} and time<={} order by time desc)
    group by type order by count desc limit 10;
""",
}
