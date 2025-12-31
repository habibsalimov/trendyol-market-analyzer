#!/usr/bin/env python3
import pymysql
from pymysql.connections import Connection
from config.db_config import db_config_parser


class DbManager:
    def __init__(self):
        self.__host = db_config_parser["SOURCE_DB"]["HOSTNAME"]
        self.__user = db_config_parser["SOURCE_DB"]["USER_NAME"]
        self.__password = db_config_parser["SOURCE_DB"]["PASSWORD"]
        self.__port = db_config_parser["SOURCE_DB"]["PORT"]
        self.__db_name = db_config_parser["SOURCE_DB"]["DB_NAME"]
        self.table_name = "trendyol_data"

    def create_connection(self) -> Connection:
        return pymysql.connect(
            host=self.__host,
            port=int(self.__port),
            user=self.__user,
            password=self.__password,
            db=self.__db_name,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
