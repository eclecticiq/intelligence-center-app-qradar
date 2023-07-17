"""Initialize services required by the application ."""
from app.init.db import init_db
from app.init.logger import init_logger

def initialize_services():
    """Initialize all the required services by the application.

    Services includes scheduler,db initialization.

    :return: Scheduler object to add or remove jobs in the future, logger object
    :rtype: tuple of Scheduler,logger
    """

    # Create logger object to be used internally by scheduler.
    logger = init_logger()

    init_db()


    return logger
