#!/usr/bin/env python3
"""
This class is not used in the project. It is just an example of how to use Selenium for web scraping.
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class TrendyolSelenium:
    def __init__(self, url="https://www.trendyol.com/gida-ve-icecek-x-c103946", category="Gıda ve İçecek"):
        self.url = url
        self.__category = category

    def __driver_init(self):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(50)
        return driver


    def __get_products(self, driver, num_products=100):
        driver.get(self.url)
        time.sleep(5)
        print(f"  Page Title: {driver.title}")
        
        # Try to dismiss overlays (blind attempts)
        try:
             driver.find_element(By.CLASS_NAME, "overlay").click()
        except:
             pass
        try:
             driver.find_element(By.CLASS_NAME, "modal-close").click()
        except:
             pass
        
        products = []
        processed_count = 0
        
        scroll_attempts = 0

        while len(products) < num_products:
            # Scroll down using Keys.PAGE_DOWN to simulate real user
            actions = ActionChains(driver)
            for _ in range(15):
                actions.send_keys(Keys.PAGE_DOWN).perform()
                time.sleep(0.5)
            
            time.sleep(2) # Wait after scroll set
            
            product_containers = driver.find_elements(By.CLASS_NAME, "product-card")
            current_count = len(product_containers)
            
            if current_count == processed_count:
                scroll_attempts += 1
                print(f"  [Scroll Retry {scroll_attempts}/3] No new products found. (Current: {len(products)})")
                if scroll_attempts >= 3:
                    print("  Max scroll retries reached. Stopping.")
                    break
                continue
            else:
                scroll_attempts = 0 # Reset on success
            
            # Process only new containers
            new_containers = product_containers[processed_count:]
            
            for container in new_containers:
                if len(products) >= num_products:
                    break
                
                try:
                    # Brand might be separate
                    try:
                        brand = container.find_element(By.CLASS_NAME, "product-brand").text
                    except:
                        brand = ""
                        
                    name_el = container.find_element(By.CLASS_NAME, "product-name").text
                    full_name = f"{brand} {name_el}".strip()
                    
                    price = container.find_element(By.CLASS_NAME, "price-value").text
                except Exception as e:
                    # If basic info is missing, skip
                    continue

                try:
                    # Description is not always available in card, using name as desc or skipping
                    description = full_name
                except:
                    description = None

                # 1. Product Image URL
                try:
                    image_element = container.find_element(By.CSS_SELECTOR, "img")
                    image_url = image_element.get_attribute("src")
                except:
                    image_url = None

                # 2. Original Price (Strikethrough)
                try:
                    original_price_element = container.find_element(By.CLASS_NAME, "prc-box-org")
                    original_price = original_price_element.text
                except:
                    # If not found, try finding any strikethrough element distinct from current price
                    try:
                         # Fallback for some layouts
                         original_price = container.find_element(By.CSS_SELECTOR, ".prc-box-org").text
                    except:
                        original_price = None

                # 3. Promotions / Badges
                promotions = []
                try:
                    # Collect text from various badge/promotion classes found
                    badges = container.find_elements(By.CSS_SELECTOR, ".promotion-text, .campaign-name, .simplified-badge-text")
                    for badge in badges:
                        text = badge.text.strip()
                        if text:
                            promotions.append(text)
                    
                    # Check for "Hızlı Teslimat" specifically if not covered above
                    if "Hızlı Teslimat" in container.text: # Simple text check if specific selector is elusive
                        if "Hızlı Teslimat" not in promotions:
                             promotions.append("Hızlı Teslimat")
                             
                    # Kargo Bedava
                    if "Kargo Bedava" in container.text and "Kargo Bedava" not in promotions:
                        promotions.append("Kargo Bedava")

                except:
                    pass
                
                promotion_text = ", ".join(promotions) if promotions else None

                # 4. Product Link
                try:
                    # The container itself is the anchor tag
                    product_link = container.get_attribute("href")
                except:
                    product_link = None

                try:
                    rating = container.find_element(By.CLASS_NAME, "average-rating").text
                except:
                    rating = None

                try:
                    review_count = container.find_element(By.CLASS_NAME, "total-count").text
                    # Remove parens if needed: (2) -> 2
                    review_count = review_count.replace("(", "").replace(")", "")
                except:
                    review_count = None

                product_info = {
                    "Ürün Adı": full_name,
                    "Fiyat": price,
                    "Orijinal Fiyat": original_price,
                    "Kampanyalar": promotion_text,
                    "Resim URL": image_url,
                    "Ürün Linki": product_link,
                    "Ürün Açıklaması": description,
                    "Ürün Kategorisi": self.__category,
                    "Değerlendirme Puanı": rating,
                    "Yorum Sayısı": review_count,
                 }

                if product_info not in products:
                     products.append(product_info)
            
            processed_count =  len(driver.find_elements(By.CLASS_NAME, "product-card"))
            print(f"  Extracted {len(products)} products so far...")
            
        return products

    def extract(self, num_products=100):
        try:
            driver = self.__driver_init()
            products = self.__get_products(driver, num_products)
            return products
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            if driver:
                driver.quit()
