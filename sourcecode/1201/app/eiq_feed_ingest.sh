#!/bin/bash
trap "kill -- -$$" EXIT
export PYTHONPATH=/opt/app-root
python -m app.ingest_feed.ingest_feed_sched 2>&1 | tee -a /opt/app-root/store/log/fetch-startup.log