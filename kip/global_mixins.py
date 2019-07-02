import logging
import datetime
import json


class LoggingMixin:
    """
    Миксина логгирования
    Сделана глобальной, так как должна использоваться в рамках всех приложений
    """

    @property
    def logger(self):
        return logging.getLogger(self.logger_name)

    def __init__(self):
        self.logger_name = '.'.join([
            self.__module__,
            self.__class__.__name__
        ])
        self.data = dict()

    def insert_log_record(self, log_record):
        """
        Формирование фиксированных полей записи лога
        """
        self.data = dict()
        self.data['logger'] = self.logger_name
        self.data['fired'] = datetime.datetime.utcnow().strftime("%d-%m-%Y %H:%M:%S.%f")
        if isinstance(log_record, dict):
            self.data.update(log_record)
        self.data = json.dumps(self.data, ensure_ascii=False)

    def warning(self, log_record, *args, **kwargs):
        self.insert_log_record(log_record)
        return self.logger.warning(self.data, *args, **kwargs)

    def error(self, log_record, *args, **kwargs):
        self.insert_log_record(log_record)
        return self.logger.error(self.data, *args, **kwargs)

    def debug(self, log_record, *args, **kwargs):
        self.insert_log_record(log_record)
        return self.logger.debug(self.data, args, kwargs)

    def exception(self, log_record, *args, **kwargs):
        self.insert_log_record(log_record)
        return self.logger.exception(self.data, *args, **kwargs)

    def info(self, log_record, *args, **kwargs):
        self.insert_log_record(log_record)
        return self.logger.info(self.data, *args, **kwargs)

    def critical(self, log_record, *args, **kwargs):
        self.insert_log_record(log_record)
        return self.logger.critical(self.data, *args, **kwargs)
