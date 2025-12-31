#!/usr/bin/env python3
import logging


class CustomLogger:
    _instances = {}

    def __new__(cls, *args, **kwargs):
        if "logger_name" not in kwargs:
            raise ValueError("You must provide a 'logger_name' argument.")

        logger_name = kwargs["logger_name"]
        if logger_name not in cls._instances:
            cls._instances[logger_name] = super().__new__(cls)
            cls._instances[logger_name].logger = logging.getLogger(logger_name)
            cls._instances[logger_name].logger.setLevel(logging.INFO)

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(name)s | %(message)s | %(funcName)s::%(pathname)s::%(lineno)d"
            )

            cls._instances[logger_name].handler = logging.StreamHandler()
            cls._instances[logger_name].handler.setFormatter(formatter)

            cls._instances[logger_name].logger.addHandler(
                cls._instances[logger_name].handler
            )

        return cls._instances[logger_name]
