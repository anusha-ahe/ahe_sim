import importlib
from django.conf import settings
from django_redis import get_redis_connection
import django
import time
import os
import logging
import ahe_log
from queue import Queue
from threading import Thread


if not settings.configured:
    settings_file = os.environ.get("DJANGO_SETTINGS_MODULE")
    settings_module = importlib.import_module(settings_file)
    django.setup()


class RedisLogHandler(logging.Handler):
    def __init__(self, redis_conn='log'):
        logging.Handler.__init__(self)
        self.redis_conn = get_redis_connection(redis_conn)

    def emit(self, record):
        try:
            msg = self.format(record)
            log_epoch = int(time.time())
            self.redis_conn.rpush(log_epoch, msg)
            self.redis_conn.expire(log_epoch, 300)
        except Exception:
            self.handleError(record)


def save_model(in_q):
    model_object = in_q.get()
    try:
        model_object.save()
    except Exception:
        print(Exception)


class DatabaseLogHandler(logging.Handler):
    def __init__(self, level=logging.NOTSET) -> None:
        super().__init__(level=level)
        self.db_time = 0
        self.rec_count = 0
        self.q = Queue()

    def emit(self, record):
        trace = None
        msg = record.getMessage()
        kwargs = {
            'logger_name': record.name,
            'level': record.levelname,
            'msg': msg,
            'trace': trace,
            'file_name': record.filename.strip(),
            'line_no': record.lineno
        }
        log_rec = ahe_log.models.EsLogger(**kwargs)
        start_time = time.time()
        self.q.put(log_rec)
        saver_thread = Thread(target=save_model, args=(self.q, ))
        saver_thread.start()
        self.db_time += time.time() - start_time
        self.rec_count += 1


def format_and_add_handler(logger, handler):
    formatter = logging.Formatter(
        '%(asctime)s~%(name)s~%(levelname)s~%(pathname)s:%(lineno)d~%(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


def add_stream_handler(logger):
    sh = logging.StreamHandler()
    sh.setLevel(logging.DEBUG)
    sh.set_name('ahe_stream_handler')
    format_and_add_handler(logger, sh)


def add_redis_handler(logger):
    rh = RedisLogHandler()
    rh.setLevel(logging.DEBUG)
    rh.set_name('ahe_redis_handler')
    format_and_add_handler(logger, rh)


logger = None


def add_db_handler():
    global logger
    dh = DatabaseLogHandler()
    dh.setLevel(logging.WARNING)
    dh.set_name('ahe_db_handler')
    logger.ahe_dh = dh
    format_and_add_handler(logger, dh)


def get_logger(name='ahe_log1', log_to_databases=False, log_all=False):
    global logger
    if logger:
        if not log_all:
            return logger
    else:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
    if log_to_databases or log_all:
        if "ahe_redis_handler" not in [handler.name for handler in logger.handlers]:
            add_redis_handler(logger)
        if "ahe_db_handler" not in [handler.name for handler in logger.handlers]:
            add_db_handler()
    if not log_to_databases or log_all:
        if "ahe_stream_handler" not in [handler.name for handler in logger.handlers]:
            add_stream_handler(logger)

    return logger


def monitor(func):
    stats = {"count": 0, "time": 0}

    def inner1(*args, **kwargs):
        stats["count"] += 1
        global logger
        start_time = time.time()
        result = func(*args, **kwargs)
        stats["time"] += time.time() - start_time
        if logger and stats["count"] % 100 == 0 and stats["count"] > 0:
            logger.debug(
                f'{func} calls: {stats["count"]} total time {stats["time"]}')
            logger.debug(
                f'{func} calls: {stats["count"]} total time {stats["time"]} time per call: {stats["time"] / stats["count"]}')
            stats["time"] = 0
            stats["count"] = 0
        return result
    return inner1
