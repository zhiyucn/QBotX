# 初始化logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]%(message)s'))
logger.addHandler(handler)

logger.info('日志初始化完成')

def get_logger(name):
    logger_temp = logging.getLogger(name)
    logger_temp.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s]%(message)s'))
    logger_temp.addHandler(handler)
    return logger_temp