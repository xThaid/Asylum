import logging

from asylum import config


def setup_logger(name, fileLevel=logging.DEBUG):
    dir = config.config['LOGGING']['log_dir']

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(dir + '/' + name + '.log')
    fh.setLevel(fileLevel)
    ch = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger
