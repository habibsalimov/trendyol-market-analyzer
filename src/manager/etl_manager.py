#!/usr/bin/env python3
# from src.analysis import DbReader
from src.analysis import Analyzer
from src.logger import CustomLogger
from src.etl import Extractor, Loader, Transformer


class ETLManager:
    def __init__(self, category="GIDA"):
        self.__extractor = Extractor(category)
        self.__transformer = Transformer()
        self.__loader = Loader()

        self.__analyzer = Analyzer()
        # self.__db_reader = DbReader()

        self.__logger = CustomLogger(logger_name="ETL Manager").logger

    def analyze(self, total_products=200):
        self.__logger.info("Analyzing data starts...")
        extracted_df = self.__extractor.extract(total_products)
        #self.__db_reader.get_data() # Enter DB credentials in .env file
        transformed_df = self.__transformer.transform(extracted_df)
        self.__analyzer.generate_report(transformed_df)
        self.__logger.info("Analyzing data finished!")

    def run_etl(self, total_products=200, output_file="output.xlsx"):
        try:
            self.__logger.info(f"ETL process starts for output: {output_file}...")
            extracted_df = self.__extractor.extract(total_products)
            transformed_df = self.__transformer.transform(extracted_df)
            transformed_df.to_excel(output_file, index=False)
            #self.__loader.load(transformed_df) # Enter DB credentials in .env file
        except Exception as e:
            self.__logger.error(f"ETL process failed: {e}")
        finally:
            self.__logger.info("ETL process finished!")