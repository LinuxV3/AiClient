import logging

log_format = '%(asctime)s -> %(levelname)s: %(message)s' # For example '2022-07-09 14:30:00,123 -> INFO: This is a test'
date_format = '%Y-%m-%d %H:%M:%S'
logger = logging.getLogger("AiClient")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
log_types = {"debug": logger.debug,
             "info": logger.info,
             "error": logger.error,
             "critical": logger.critical,
             'warning': logger.warning,
             'warn': logger.warn,
             'log': logger.log}


def log(dest: str, log_type='INFO') -> None:
    log_type = log_type.lower()
    if log_type in log_types:
        log_types[log_type](dest)
    else:
        logger.debug(dest)


