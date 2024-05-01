import os 
import logging

from ..logger import CustomFormatter

logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

# logger.debug("debug message")
# logger.info("Warning: Email has not been sent......")
# logger.warning("warning message")
# logger.error("error message")
# logger.critical("critical message")

def print_something():
    logger.info('for Aram')