#!/usr/bin/env python3
from typing import Dict, Any
from bs4 import BeautifulSoup


class ExtractHelper:
    def __init__(self, category):
        self.__category = category

    def extract_products_from_html(self, html_content: str):
        soup = BeautifulSoup(html_content, "html.parser")
        product_containers = soup.find_all("div", class_="p-card-wrppr")
        products = []

        for container in product_containers:
            name = container.find("span", class_="prdct-desc-cntnr-name").text
            price = container.find("div", class_="prc-box-dscntd").text

            try:
                description = container.find("div", class_="product-desc-sub-text").text
            except:
                description = None

            try:
                rating = container.find("span", class_="ratingCount").text
            except:
                rating = None

            try:
                review_count = container.find("span", class_="ratingCount").text
            except:
                review_count = None

            product_info = {
                "Ürün Adı": name,
                "Fiyat": price,
                "Ürün Açıklaması": description,
                "Ürün Kategorisi": self.__category,
                "Değerlendirme Puanı": rating,
                "Yorum Sayısı": review_count,
            }

            products.append(product_info)

        return products

    def extract_products_from_json(self, json_data: Dict[str, Any]):
        products = []

        for product in json_data["result"]["products"]:
            name = product["name"]
            price = product["price"]["discountedPrice"]
            description = product["categoryHierarchy"]

            try:
                rating = product["ratingScore"]["averageRating"]
            except:
                rating = None

            try:
                review_count = product["ratingScore"]["totalCount"]
            except:
                review_count = None

            product_info = {
                "Ürün Adı": name,
                "Fiyat": price,
                "Ürün Açıklaması": description,
                "Ürün Kategorisi": self.__category,
                "Değerlendirme Puanı": rating,
                "Yorum Sayısı": review_count,
            }

            products.append(product_info)

        return products
