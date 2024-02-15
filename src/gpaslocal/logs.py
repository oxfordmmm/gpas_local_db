import sys
import click_log  # type: ignore
import logging
import progressbar


class ErrorCheckHandler(logging.StreamHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.error_occurred = False

    def emit(self, record):
        if record.levelno == logging.ERROR:
            self.error_occurred = True
        # we don't want to emit anything, as that is handle by the click handler,
        # so do not call super
        # super().emit(record)


class CustomLogger(logging.Logger):
    @property
    def error_occurred(self) -> bool:
        return any(
            handler.error_occurred
            for handler in self.handlers
            if isinstance(handler, ErrorCheckHandler)
        )


# we need to wrap the stderr with the progressbar
# so that logging is displayed correctly
progressbar.streams.wrap_stderr()

logging.setLoggerClass(CustomLogger)
logger = logging.getLogger("gpas-local")
click_log.basic_config(logger)

error_check_handler = ErrorCheckHandler(stream=sys.stderr)

logger.addHandler(error_check_handler)
logger.setLevel(logging.INFO)
