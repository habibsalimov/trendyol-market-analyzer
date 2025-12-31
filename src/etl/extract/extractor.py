#!/usr/bin/env python3
import re
import pandas as pd
from typing import Optional
from src.logger import CustomLogger
from .trendyol_selenium import TrendyolSelenium
from config import category_config_parser


class Extractor:
    def __init__(self, category: str):
        self.__url = category_config_parser[category]["URL"]
        self.__category_name = category_config_parser[category]["NAME"]
        # self.__base_api_url = category_config_parser[category]["BASE_API_URL"] # Not used in Selenium
        # self.__extract_helper = ExtractHelper(category_config_parser[category]["NAME"]) # Not used in Selenium

        self.__logger = CustomLogger(logger_name="Trendyol Scraper").logger
        self.__selenium_extractor = TrendyolSelenium(self.__url, self.__category_name)

    def extract(self, total_products: int = 100) -> pd.DataFrame:
        self.__logger.info("Extracting products from Trendyol using Selenium...")
        products = self.__selenium_extractor.extract(total_products)
        
        if not products:
             self.__logger.warning("No products extracted!")
             return pd.DataFrame()

        self.__logger.info(f"Total products extracted: {len(products)}")
        return pd.DataFrame(products)