#!/usr/bin/env python3
import pandas as pd
from src.manager import DbManager
from pymysql.err import MySQLError
from src.logger import CustomLogger


class Loader(DbManager):
    def __init__(self):
        self.__logger = CustomLogger(logger_name="Loader").logger
        super().__init__()

    def __create_table_if_not_exists(self, cursor, df_columns):
        self.__logger.info(f"Creating {self.table_name} table if not exists")
        cursor.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self.table_name} (
                {', '.join([f"{col} TEXT" for col in df_columns])}
            )
        """
        )

    def load(self, df: pd.DataFrame):
        self.__logger.info(f"Loading data into {self.table_name} table")
        try:
            connection = self.create_connection()
            cursor = connection.cursor()

            self.__create_table_if_not_exists(cursor, df.columns)

            for _, row in df.iterrows():
                sql = f"INSERT INTO {self.table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s'] * len(row))})"
                cursor.execute(sql, tuple(row))

            connection.commit()
            cursor.close()
            connection.close()
            self.__logger.info(f"Data inserted successfully into {self.table_name}")
        except MySQLError as e:
            self.__logger.error(f"Error occurred: {e}")
