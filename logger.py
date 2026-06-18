import logging
from logging.handlers import RotatingFileHandler

def get_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    handler = RotatingFileHandler(
        filename="app.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger