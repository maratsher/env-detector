import logging
import logging.config

from env_detector.config import APP_SETTINGS


def create_logger(name, log_file_name, log_level=None):
    logging_enabled = APP_SETTINGS.LOGGING

    if not logging_enabled:
        logging.basicConfig(level=logging.WARNING)
        return None

    logger = logging.getLogger(name)
    logger.setLevel(
        log_level if log_level else logging.DEBUG if APP_SETTINGS.DEBUG else logging.INFO)

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = logging.FileHandler(
        f'env_logs/{log_file_name}.log', mode='w')
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logger.level)

    logger.addHandler(file_handler)

    logger.propagate = False

    return logger


logger = create_logger('service_logger', 'service')
