import logging
import sys
from pathlib import Path

def setup_logger(name: str, log_level:str="INFO") -> logging.Logger:
    """ 
    Set up a logger with constant formatting
    """
    logger=logging.getLogger(name)

    if logger.handlers:
        return logger
    logger.setLevel(getattr(logging, log_level.upper()))

    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHanler(console_handler)


    log_file = Path("logs") / f"{name}.log"
    log_file.parent.mkdir(exist_ok=True)

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
