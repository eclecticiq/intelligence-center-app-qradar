"""Initialize services required by the application ."""
from app.init.db import init_db
from app.init.logger import init_logger
from app.init.scheduler import init_scheduler


def initialize_services():
    """Initialize all the required services by the application.

    Services includes scheduler,db initialization.

    :return: Scheduler object to add or remove jobs in the future, logger object
    :rtype: tuple of Scheduler,logger
    """
    init_db()

    # Create logger object to be used internally by scheduler.
    logger = init_logger()

    # Initialize Scheduler
    scheduler = init_scheduler()

    return scheduler, logger
