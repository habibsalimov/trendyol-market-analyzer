#!/usr/bin/env python3
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from src.logger import CustomLogger


class Analyzer:
    def __init__(self):
        self.df = None
        self.output_dir = os.path.join(os.getcwd(), "images")
        #self.output_dir = "/path/in/container"  # Update to the bind-mounted path

        self.__logger = CustomLogger(logger_name="Analysis").logger

        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def __check_columns(self):
        required_columns = ["Fiyat", "Değerlendirme Puanı", "Yorum Sayısı", "Ürün Adı"]
        for col in required_columns:
            if col not in self.df.columns:
                raise ValueError(f"{col} sütunu bulunamadı.")

    def __get_most_expensive_and_cheapest_products(self):
        most_expensive = self.df.loc[self.df["Fiyat"].idxmax()]
        cheapest = self.df.loc[self.df["Fiyat"].idxmin()]
        return most_expensive, cheapest

    def __get_highest_rated_products(self):
        return self.df.loc[self.df["Değerlendirme Puanı"].idxmax()]

    def __get_most_reviewed_products(self):
        return self.df.loc[self.df["Yorum Sayısı"].idxmax()]

    def __get_average_price_by_brand(self):
        return self.df.groupby("Ürün Adı")["Fiyat"].mean().reset_index()

    def generate_report(self, df):
        self.df = df
        self.__check_columns()
        self.__logger.info("Creating values from data...")
        most_expensive, cheapest = self.__get_most_expensive_and_cheapest_products()
        highest_rated = self.__get_highest_rated_products()
        most_reviewed = self.__get_most_reviewed_products()
        avg_price_by_brand = self.__get_average_price_by_brand()

        self.__logger.info("Creating visualizations...")
        sns.set(style="whitegrid")

        # Average Price by Brand
        plt.figure(figsize=(10, 6))
        sns.barplot(
            x="Fiyat",
            y="Ürün Adı",
            data=avg_price_by_brand.sort_values(by="Fiyat", ascending=False).head(10),
        )
        plt.title("Ortalama Fiyatlar (Markalara Göre)")
        plt.xlabel("Ortalama Fiyat")
        plt.ylabel("Marka")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'average_price_by_brand.png'))
        plt.show()

        # Distribution of Product Prices
        plt.figure(figsize=(10, 6))
        sns.histplot(self.df["Fiyat"], kde=True)
        plt.title("Ürün Fiyat Dağılımı")
        plt.xlabel("Fiyat")
        plt.ylabel("Frekans")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'price_distribution.png'))
        plt.show()

        # Top N Products by Review Count
        top_reviewed_products = self.df.nlargest(10, "Yorum Sayısı")
        plt.figure(figsize=(10, 6))
        sns.barplot(x="Yorum Sayısı", y="Ürün Adı", data=top_reviewed_products)
        plt.title("En Çok Yorum Alan Ürünler")
        plt.xlabel("Yorum Sayısı")
        plt.ylabel("Ürün Adı")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'top_reviewed_products.png'))
        plt.show()

        # Rating Distribution
        plt.figure(figsize=(10, 6))
        sns.histplot(self.df["Değerlendirme Puanı"], kde=True)
        plt.title("Değerlendirme Puanı Dağılımı")
        plt.xlabel("Değerlendirme Puanı")
        plt.ylabel("Frekans")
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, 'rating_distribution.png'))
        plt.show()

        print(
            f"""
        En Pahalı Ürün:
        {most_expensive.to_dict()}
        En Ucuz Ürün:
        {cheapest.to_dict()}
        En Yüksek Puanlı Ürün:
        {highest_rated.to_dict()}
        En Çok Yorum Alan Ürün:
        {most_reviewed.to_dict()}"""
        )
