import logging
from gui.logging import get_logger
from gui.data_functions.data_format.format import process_raptr_zip
from gui.models import Data

logger = get_logger(__file__, log_level=logging.INFO)


def add_project_from_zip(filename):
    logger.info("Processing RAPTR file")
    df = process_raptr_zip(filename)
    logger.info("Done")
    return df

