import sys
import logging

class ErrorCheckHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_occurred = False

    def emit(self, record):
        if record.levelno == logging.ERROR:
            self.error_occurred = True
        super().emit(record)

logger = logging.getLogger('gpas-local')

log_format = logging.Formatter('%(levelname)s: %(message)s')
stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setFormatter(log_format)

error_check_handler = ErrorCheckHandler(stream=sys.stderr)
error_check_handler.setFormatter(log_format)

logger.addHandler(stream_handler)
logger.addHandler(error_check_handler)
logger.setLevel(logging.INFO)

def error_occurred() -> bool:
    return error_check_handler.error_occurred
