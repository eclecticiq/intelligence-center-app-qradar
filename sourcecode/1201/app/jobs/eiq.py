"""Add Jobs."""
from datetime import datetime
from app.collector.eiq_data import EIQApi
from app.configs.datastore import DATA_STORE_DIR, DATA_STORE_SETUP_FILE
from app.constants.general import LOG_LEVEL_DEBUG, LOG_LEVEL_INFO
from app.constants.messages import (
    SCHEDULER_CONFIG_LOG,
    SCHEDULER_PAUSED,
    SCHEDULER_RESCHEDLED,
    SCHEDULER_RESUMED,
    SCHEDULER_STARTED,
    SEND_PULL_EVENT_CALLED,
)
from app.constants.scheduler import (
    COLLECT_OBSERVABLES_ID_JOB,
    SCHEDULER_ID,
    SCHEDULER_INTERVAL,
    SCHEDULER_SECONDS,
    SCHEDULER_TRIGGER,
)
from app.datastore import read_data_store
from qpylib import qpylib


def send_pull_event():
    """Add job to the scheduler for fetching data from eiq."""
    from app import scheduler  # pylint: disable=C0415

    qpylib.log(SEND_PULL_EVENT_CALLED)

    setup_data = read_data_store(DATA_STORE_DIR, DATA_STORE_SETUP_FILE)

    # Pause the jobs
    if scheduler.is_running():
        scheduler.pause()
        qpylib.log(SCHEDULER_PAUSED, level=LOG_LEVEL_INFO)

    schedule = {SCHEDULER_TRIGGER: SCHEDULER_INTERVAL}

    if SCHEDULER_INTERVAL in setup_data and setup_data[SCHEDULER_INTERVAL]:
        # Add scheduler seconds provided in configurations
        interval = setup_data[SCHEDULER_INTERVAL]
        schedule[SCHEDULER_SECONDS] = int(interval)
        schedule[SCHEDULER_ID] = COLLECT_OBSERVABLES_ID_JOB
        schedule["next_run_time"] = datetime.now()
        qpylib.log(
            SCHEDULER_CONFIG_LOG.format(job=COLLECT_OBSERVABLES_ID_JOB),
            level=LOG_LEVEL_DEBUG,
        )

        # Check if observables collection job exists
        if scheduler.is_job_exists(COLLECT_OBSERVABLES_ID_JOB):
            # Job already exists, remove it
            scheduler.remove_job(COLLECT_OBSERVABLES_ID_JOB)
            qpylib.log(
                SCHEDULER_RESCHEDLED.format(job=COLLECT_OBSERVABLES_ID_JOB),
                level=LOG_LEVEL_DEBUG,
            )

        # Add Job to the job store
        eiq_api = EIQApi()
        scheduler.add_job(eiq_api.get_observables, schedule)

    # start scheduled jobs
    if scheduler.is_paused():
        scheduler.resume()
        qpylib.log(SCHEDULER_RESUMED, level=LOG_LEVEL_DEBUG)
    elif not scheduler.is_running():
        scheduler.start()
        qpylib.log(SCHEDULER_STARTED, level=LOG_LEVEL_INFO)
