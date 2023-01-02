import hx
import os
import logging
from time import perf_counter
import sys
import traceback
from logging import Handler, LogRecord


def get_logger():
    return logging.getLogger("aig_rater_model_logger")


def clear_handlers():
    log = get_logger()
    log.handlers = [h for h in log.handlers if isinstance(h, logging.StreamHandler)]


def init_log(hxd_message_node, logging_level='DEBUG', hxd_message_node_alt=None, msg_only=True):
    # initialise logger
    log = get_logger()
    # log.propagate = False

    # if not lowest level, set level for filtering message output
    try:
        if logging_level != 'DEBUG':
            sel_log_level = getattr(logging, logging_level)
        else:
            sel_log_level = logging.DEBUG
    except Exception:
        # [TODO] - work out why hx doesn't like setting to DEBUG
        print('Cant set logging level')

    log.setLevel(sel_log_level)

    # clear existing hxLogHandler
    log.handlers = [h for h in log.handlers if not isinstance(h, hxLogHandler)]
    # updated clearing approach to only clearing hxLogHandler

    # add basic output to all for writing to console for all info
    logging.basicConfig(level=logging.DEBUG, stream=sys.stderr)
    # updated stream to stderr instead of stdout, on advice from hx

    # add hxLogHandler
    logHandler = hxLogHandler(hxd_message_node, sel_log_level, msg_only)
    log.addHandler(logHandler)

    if hxd_message_node_alt is not None:
        logHandler_alt = hxLogHandler(hxd_message_node_alt, sel_log_level, True)
        log.addHandler(logHandler_alt)

    return log


class hxLogHandler(Handler):
    """
    Custom handler to save items to hxd message or validation errors depending on outcome
    """
    def __init__(self, hxd_message_node, logging_level, msg_only=True):
        logging.Handler.__init__(self)
        self.hxd_message_node = hxd_message_node
        self.level = logging_level
        self.init_time = perf_counter()
        self.msg_only = msg_only
        self.msg_count = 0

    # default handler for incoming messages from log, called by log.DEBUG etc
    def emit(self, record: LogRecord):
        # call format - if set
        self.format(record)

        # add stack trace if it exists
        record.stack_info = traceback.format_exc()

        # filter according to logging_level set in initialisation
        if record.levelno >= self.level:

            # if not self.msg_only:
            dict_record = {
                "args": str(record.args),  # AJC: data schema expects this to be a string
                "asctime": int(10000 * (perf_counter() - self.init_time)) / 10000,
                "exc_info": str(record.exc_info),  # AJC: data schema expects this to be a string
                "exc_text": record.exc_text,
                "filename": record.filename,
                "funcName": record.funcName,
                "levelname": record.levelname,
                "levelno": record.levelno,
                "lineno": record.lineno,
                "module": record.module,
                "msecs": record.msecs,
                "msg": record.msg,
                "name": record.name,
                "pathname": record.pathname,
                "process": record.process,
                "processName": record.processName,
                "relativeCreated": record.relativeCreated,
                "stack_info": record.stack_info
            }
            # else:
            #     dict_record = {
            #         "messageType": str(record.exc_info) + str(record.exc_text),
            #         "message": str(record.msg),
            #         "messageId": str(self.msg_count)
            #     }

            self.msg_count += 1

            self.hxd_message_node.append(dict_record)
