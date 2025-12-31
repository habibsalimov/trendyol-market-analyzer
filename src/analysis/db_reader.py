#!/usr/bin/env python3
import pandas as pd
from src.manager import DbManager


class DbReader(DbManager):
    def __init__(self):
        super().__init__()

    def get_data(self):
        query = f"SELECT * FROM {self.table_name}"
        try:
            connection = self.create_connection()
            df = pd.read_sql(query, connection)
            connection.close()
            return df
        except Exception as e:
            print(f"Error occurred: {e}")
            return None