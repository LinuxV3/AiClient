import logging

log_format = '%(asctime)s -> %(levelname)s: %(message)s' # For example '2022-07-09 14:30:00,123 -> INFO: This is a test'
date_format = '%Y-%m-%d %H:%M:%S'
log_events = False
logger = logging.getLogger("AiClient")
logger.setLevel(logging.DEBUG)
logging.basicConfig(level=logging.DEBUG, format=log_format, datefmt=date_format)
log_types = {"debug": logger.debug,
             "info": logger.info,
             "error": logger.error,
             "critical": logger.critical,
             'warning': logger.warning,
             'warn': logger.warning,
             'log': logger.log}


def log(dest: str, log_type: str='INFO') -> None:
    global log_events
    if not log_events:
        return
    log_type = log_type.lower()
    if log_type in log_types:
        log_types[log_type](dest)
    else:
        logger.debug(dest)


def set_log_level(log_level: str | bool):
    global log_events
    if not log_level or log_level.lower() == 'false':
        log_events = False
        logging.disable(logging.CRITICAL)
        return
    else:
        log_events = True
    log_level = log_level.upper()
    if log_level in ['DEBUG', 'INFO', 'ERROR', 'CRITICAL', 'WARNING', 'WARN']:
        log_level = {'DEBUG': logging.DEBUG, 'INFO': logging.INFO, 'ERROR': logging.ERROR,
                     'CRITICAL': logging.CRITICAL, 'WARNING': logging.WARNING, 'WARN': logging.WARN}[log_level]
    logging.basicConfig(level=log_level, format=log_format, datefmt=date_format)
    logger.setLevel(log_level)


