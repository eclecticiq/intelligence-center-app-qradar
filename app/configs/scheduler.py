"""Scheduler Configurations."""

SCHEDULER_JOBSTORE_TYPE = "sqlalchemy"
SCHEDULER_JOBSTORE_DB = "sqlite://"
SCHEDULER_JOBSTORE_DB_PATH = "store"
SCHEDULER_JOBSTORE_DB_NAME = "scheduler.db"
SCHEDULER_EXECUTOR_TYPE = "threadpool"
SCHEDULER_EXECUTOR_MAX_WORKERS = 5
SCHEDULER_JOB_DEFAULTS_COALESCE = True
SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES = 1
