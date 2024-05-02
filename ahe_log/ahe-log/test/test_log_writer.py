import logging
import time
import ahe_log
from django_redis import get_redis_connection
from inspect import currentframe
from asgiref.sync import sync_to_async, async_to_sync
import asyncio

LOGGER = "test_logger"
MESSAGE = "test_1"


def test_should_work_as_logging(caplog):
    logger = ahe_log.get_logger(LOGGER)
    logger.warning('Warning msg')
    logger.debug('Debug msg')
    logger.error('Error msg')
    assert 'Warning msg' in caplog.text
    assert 'Debug msg' in caplog.text
    assert 'Error msg' in caplog.text


# test = AheLogger(LOGGER, "redis")
# redis_db = "redis"
# redis_conn = get_redis_connection(redis_db)
file_name = __file__.split("/")[-1]


def test_should_crate_single_logger():
    test1 = ahe_log.get_logger(LOGGER)
    test2 = ahe_log.get_logger("abc")
    test3 = ahe_log.get_logger()
    assert test1 is test2
    assert test1 is test3


def test_should_contain_file_name(caplog):
    logger = ahe_log.get_logger(LOGGER)
    logger.warning('Warning msg')
    print("caplog", caplog.text)
    assert 'test_log_writer.py' in caplog.text
    assert LOGGER in caplog.text


def test_should_contain_line(caplog):
    logger = ahe_log.get_logger(LOGGER)
    cf = currentframe()
    line_no = cf.f_lineno
    logger.warning('Warning msg')
    print(caplog.text)
    assert f'{line_no + 1} Warning msg' in caplog.text


def test_should_add_debug_in_redis():
    cf = currentframe()
    logger1 = ahe_log.get_logger(LOGGER, True, True)
    line_no = cf.f_lineno
    logger1.debug(MESSAGE)
    redis_conn = get_redis_connection('log')
    message = redis_conn.lrange(int(time.time()), 0, 5)[-1].decode("utf-8")
    print(message)
    assert LOGGER in message
    assert "DEBUG" in message
    assert file_name in message
    assert f':{line_no + 1}~{MESSAGE}' in message


def test_should_add_warning_in_database():
    before_db_count = ahe_log.models.EsLogger.objects.filter(
        logger_name=LOGGER).count()
    logger1 = ahe_log.get_logger(LOGGER, True)
    logger1.error(MESSAGE)
    start_time = time.time()
    while before_db_count + 1 != ahe_log.models.EsLogger.objects.filter(
            logger_name=LOGGER).count():
        if time.time() > start_time + 10:
            assert False


def test_should_log_db_error_fast():
    before_db_count = ahe_log.models.EsLogger.objects.filter(
        logger_name=LOGGER).count()
    logger1 = ahe_log.get_logger(LOGGER, True)
    start_time = time.time()
    test_count = 20
    for _ in range(test_count):
        logger1.error(MESSAGE)
    time_taken = time.time() - start_time
    start_time = time.time()
    while before_db_count + test_count != ahe_log.models.EsLogger.objects.filter(
            logger_name=LOGGER).count():
        if time.time() > start_time + 200:
            print("db time =", logger1.ahe_dh.db_time, logger1.ahe_dh.rec_count)
            assert False
    assert time_taken < 2


def test_should_add_debug_msg_fast():
    logger1 = ahe_log.get_logger(LOGGER)
    start_time = time.time()
    for _ in range(1000):
        logger1.debug(MESSAGE)
    end_time = time.time()
    print(end_time - start_time)
    assert end_time - start_time < 2


def test_log_monitor(caplog):
    @ahe_log.monitor
    def dummy_func():
        time.sleep(.002)
    for _ in range(100):
        dummy_func()
    print(caplog.text)
    assert 'time per call:' in caplog.text


if __name__ == '__main__':
    logger1 = ahe_log.get_logger(LOGGER)
    logger1.debug(MESSAGE)
    test_log_monitor(None)
