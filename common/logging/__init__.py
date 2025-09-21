from loguru import logger
from common.logging.mongo_sink import mongo_sink


logger.add(lambda msg: print(msg, end=""), colorize=True, level="INFO")

logger.add(mongo_sink, level="INFO", serialize=False)
