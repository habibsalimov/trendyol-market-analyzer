#!/usr/bin/env python3
import pandas as pd
from src.logger import CustomLogger


class Transformer:
    def __init__(self):
        self.__logger = CustomLogger(logger_name="Transformer").logger

    @staticmethod
    def check_columns(df: pd.DataFrame) -> pd.DataFrame:
        required_columns = ["Fiyat", "Değerlendirme Puanı", "Yorum Sayısı", "Ürün Adı"]
        for column in required_columns:
            if column not in df.columns:
                raise ValueError(f"{column} column is missing.")
        return df

    @staticmethod
    def clean_price(df: pd.DataFrame) -> pd.DataFrame:
        df["Fiyat"] = df["Fiyat"].astype(str)
        df["Fiyat"] = (
            df["Fiyat"].str.replace(" TL", "").str.replace(",", "").astype(float)
        )
        df.loc[df["Fiyat"] > 1000, "Fiyat"] = df["Fiyat"] / 100
        return df

    @staticmethod
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        df["Fiyat"].fillna(df["Fiyat"].mean(), inplace=True)
        df["Değerlendirme Puanı"].fillna(0, inplace=True)
        df["Yorum Sayısı"].fillna(0, inplace=True)
        df["Ürün Adı"].fillna("Bilinmeyen Ürün", inplace=True)
        if "Ürün Linki" in df.columns:
            df["Ürün Linki"].fillna("", inplace=True)
        return df

    @staticmethod
    def clean_rating_and_reviews(df: pd.DataFrame) -> pd.DataFrame:
        df["Değerlendirme Puanı"] = df["Değerlendirme Puanı"].astype(str)
        df["Yorum Sayısı"] = df["Yorum Sayısı"].astype(str)
        # Remove non-numeric characters
        df["Değerlendirme Puanı"] = df["Değerlendirme Puanı"].str.replace(
            "[^0-9.]", "", regex=True
        )
        df["Yorum Sayısı"] = df["Yorum Sayısı"].str.replace("[^0-9]", "", regex=True)
        return df

    @staticmethod
    def convert_data_types(df: pd.DataFrame) -> pd.DataFrame:
        df["Değerlendirme Puanı"] = df["Değerlendirme Puanı"].astype(float)
        df["Yorum Sayısı"] = df["Yorum Sayısı"].astype(int)
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            self.__logger.info("Transformation starts...")
            df = self.check_columns(df)
            df = self.clean_price(df)
            df = self.handle_missing_values(df)
            df = self.clean_rating_and_reviews(df)
            df = self.convert_data_types(df)
            self.__logger.info("Transformation completed.")
            return df
        except Exception as e:
            self.__logger.error(f"Transformation failed: {e}")
            raise
