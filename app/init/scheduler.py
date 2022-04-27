"""Initializing Scheduler ."""
import os

from app.configs.scheduler import (
    SCHEDULER_EXECUTOR_MAX_WORKERS,
    SCHEDULER_EXECUTOR_TYPE,
    SCHEDULER_JOB_DEFAULTS_COALESCE,
    SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES,
    SCHEDULER_JOBSTORE_DB,
    SCHEDULER_JOBSTORE_DB_NAME,
    SCHEDULER_JOBSTORE_DB_PATH,
    SCHEDULER_JOBSTORE_TYPE,
)
from app.constants.scheduler import (
    SCHEDULER_CONFIG_DIR,
    SCHEDULER_CONFIG_FILE,
    SCHEDULER_LABEL_COALESCE,
    SCHEDULER_LABEL_DEFAULT,
    SCHEDULER_LABEL_MAX_INSTANCES,
    SCHEDULER_LABEL_MAX_WORKERS,
    SCHEDULER_LABEL_TYPE,
    SCHEDULER_LABEL_URL,
    SCHEDULER_PARENT_DIR,
)
from app.utils.files import read_yaml_configurations
from pyscheduler.schedule import Schedule


class SchedulerObject:
    """Initialize the Scheduler Object."""

    _instance = None  # type: Schedule
    schedule = None  # type: Schedule

    def __init__(self):
        """Initialize the Scheduler Object.

        :raises RuntimeError: This follows Singleton design pattern, hence creation of the instance should not be allowed via instance directly
        """
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        """Instance method to create the instance of Scheduler class.

        This follows Singleton design pattern

        :return: Scheduler instance
        :rtype: Scheduler
        """
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls.schedule = Schedule()
        return cls._instance

    def get_scheduler(self):
        """Get scheduler object."""
        return self.schedule


def init_scheduler():
    """Read scheduler configurations.

    :return: Scheduler configurations object
    :rtype: Schedule
    """
    app_root_parent_dir = os.getcwd()

    db_path = os.path.join(
        app_root_parent_dir, SCHEDULER_JOBSTORE_DB_PATH, SCHEDULER_JOBSTORE_DB_NAME
    )  # pwd/store/scheduler.db

    jobstore_url = (
        f"{SCHEDULER_JOBSTORE_DB}//{db_path}"  # sqlite:////pwd/store/scheduler.db
    )

    jobstores = {
        SCHEDULER_LABEL_DEFAULT: {
            SCHEDULER_LABEL_TYPE: SCHEDULER_JOBSTORE_TYPE,
            SCHEDULER_LABEL_URL: jobstore_url,
        }
    }  # {"default":{"type":"sqlalchemy","url":"sqlite:////cwd/store/scheduler.db"}}
    executors = {
        SCHEDULER_LABEL_DEFAULT: {
            SCHEDULER_LABEL_TYPE: SCHEDULER_EXECUTOR_TYPE,
            SCHEDULER_LABEL_MAX_WORKERS: SCHEDULER_EXECUTOR_MAX_WORKERS,
        }
    }  # {"default":{"type":threadpool,"max_workers":5}}
    job_defaults = {
        SCHEDULER_LABEL_COALESCE: SCHEDULER_JOB_DEFAULTS_COALESCE,
        SCHEDULER_LABEL_MAX_INSTANCES: SCHEDULER_JOB_DEFAULTS_MAX_INSTANCES,
    }  # {"coalesce":True, max_instances:1}

    # Create scheduler object
    scheduler_obj = SchedulerObject.instance()
    schedule = scheduler_obj.get_scheduler()

    # Add configurations
    schedule.add_configurations(
        jobstores=jobstores, executors=executors, job_defaults=job_defaults
    )

    # Add jobs to schedule
    filename = os.path.join(
        SCHEDULER_PARENT_DIR, SCHEDULER_CONFIG_DIR, SCHEDULER_CONFIG_FILE
    )  # filename:app/configs/schedule.yaml
    configurations = read_yaml_configurations(filename)
    schedule.start()
    schedule.pause()

    if schedule.is_job_exists("delete_observables_job"):
        # Job already exists, remove it)

        schedule.remove_job("delete_observables_job")
    schedule.add_jobs(configurations)
    schedule.resume()
    return schedule
