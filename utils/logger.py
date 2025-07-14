import logging


logger = logging.getLogger('logger')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)