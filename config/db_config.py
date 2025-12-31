#!/usr/bin/env python3
import configparser
from decouple import config

db_config_parser = configparser.ConfigParser()

db_config_parser["SOURCE_DB"] = {
    "USER_NAME": config("DATAWAREHOUSE_USER"),
    "PASSWORD": config("DATAWAREHOUSE_PASSWORD"),
    "HOSTNAME": config("DATAWAREHOUSE_HOST"),
    "PORT": config("PORT_NUMBER"),
    "DB_NAME": config("DB_NAME"),
}
