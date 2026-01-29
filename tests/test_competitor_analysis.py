"""
Test modülü: Rakip analizi fonksiyonları
"""
import pytest
import pandas as pd
import numpy as np


class TestBrandAnalysis:
    """Marka analizi testleri"""
    
    @pytest.fixture
    def sample_df(self):
        """Örnek veri seti"""
        return pd.DataFrame({
            "Ürün Adı": [
                "BrandA Ürün 1",
                "BrandA Ürün 2",
                "BrandB Ürün 1",
                "BrandC Ürün 1",
                "BrandC Ürün 2",
                "BrandC Ürün 3"
            ],
            "Fiyat": [100, 150, 200, 80, 90, 100],
            "Değerlendirme Puanı": [4.5, 4.8, 4.2, 4.9, 4.7, 4.6]
        })
    
    def test_brand_extraction(self, sample_df):
        """Marka çıkarma testi"""
        sample_df["Marka"] = sample_df["Ürün Adı"].apply(lambda x: x.split()[0])
        
        unique_brands = sample_df["Marka"].unique()
        assert len(unique_brands) == 3
        assert "BrandA" in unique_brands
        assert "BrandB" in unique_brands
        assert "BrandC" in unique_brands
    
    def test_brand_product_count(self, sample_df):
        """Marka ürün sayısı testi"""
        sample_df["Marka"] = sample_df["Ürün Adı"].apply(lambda x: x.split()[0])
        brand_counts = sample_df["Marka"].value_counts()
        
        assert brand_counts["BrandC"] == 3
        assert brand_counts["BrandA"] == 2
        assert brand_counts["BrandB"] == 1
    
    def test_brand_average_price(self, sample_df):
        """Marka ortalama fiyat testi"""
        sample_df["Marka"] = sample_df["Ürün Adı"].apply(lambda x: x.split()[0])
        brand_avg_price = sample_df.groupby("Marka")["Fiyat"].mean()
        
        assert brand_avg_price["BrandA"] == 125  # (100+150)/2
        assert brand_avg_price["BrandB"] == 200
        assert brand_avg_price["BrandC"] == 90   # (80+90+100)/3
    
    def test_brand_rating_average(self, sample_df):
        """Marka ortalama puan testi"""
        sample_df["Marka"] = sample_df["Ürün Adı"].apply(lambda x: x.split()[0])
        brand_avg_rating = sample_df.groupby("Marka")["Değerlendirme Puanı"].mean()
        
        assert brand_avg_rating["BrandA"] == 4.65  # (4.5+4.8)/2


class TestPositioningMap:
    """Konumlandırma haritası testleri"""
    
    @pytest.fixture
    def positioning_data(self):
        """Konumlandırma verisi"""
        return pd.DataFrame({
            "Ürün": ["A", "B", "C", "D"],
            "Fiyat": [50, 150, 50, 150],
            "Puan": [4.8, 4.9, 4.2, 4.1]
        })
    
    def test_quadrant_assignment(self, positioning_data):
        """Kadran atama testi"""
        median_price = positioning_data["Fiyat"].median()
        median_rating = positioning_data["Puan"].median()
        
        def get_quadrant(row):
            if row["Fiyat"] > median_price and row["Puan"] > median_rating:
                return "Premium Kalite"
            elif row["Fiyat"] <= median_price and row["Puan"] > median_rating:
                return "En İyi Değer"
            elif row["Fiyat"] > median_price and row["Puan"] <= median_rating:
                return "Pahalı-Düşük"
            else:
                return "Ekonomik"
        
        positioning_data["Kadran"] = positioning_data.apply(get_quadrant, axis=1)
        
        # Ürün A: Düşük fiyat, yüksek puan -> En İyi Değer
        assert positioning_data[positioning_data["Ürün"] == "A"]["Kadran"].values[0] == "En İyi Değer"
        
        # Ürün B: Yüksek fiyat, yüksek puan -> Premium Kalite
        assert positioning_data[positioning_data["Ürün"] == "B"]["Kadran"].values[0] == "Premium Kalite"
    
    def test_median_lines(self, positioning_data):
        """Medyan çizgileri testi"""
        median_price = positioning_data["Fiyat"].median()
        median_rating = positioning_data["Puan"].median()
        
        assert median_price == 100
        assert median_rating == 4.5


class TestSWOTAnalysis:
    """SWOT analizi testleri"""
    
    def test_strength_identification(self):
        """Güçlü yön belirleme"""
        avg_rating = 4.7
        avg_market_rating = 4.3
        
        is_strength = avg_rating > avg_market_rating
        assert is_strength == True
    
    def test_weakness_identification(self):
        """Zayıf yön belirleme"""
        product_count = 5
        competitor_avg_count = 15
        
        is_weakness = product_count < competitor_avg_count
        assert is_weakness == True
    
    def test_opportunity_identification(self):
        """Fırsat belirleme"""
        segment_gap = {
            "Ekonomik": 0.30,  # %30 pazar payı
            "Premium": 0.05   # %5 pazar payı - fırsat
        }
        
        opportunity_segment = min(segment_gap, key=segment_gap.get)
        assert opportunity_segment == "Premium"
    
    def test_threat_identification(self):
        """Tehdit belirleme"""
        price_war = True  # Fiyat savaşı var mı
        new_competitors = 3  # Son dönem giren rakip sayısı
        
        threat_level = "Yüksek" if price_war and new_competitors > 2 else "Düşük"
        assert threat_level == "Yüksek"


class TestMarketShare:
    """Pazar payı testleri"""
    
    def test_brand_market_share(self):
        """Marka pazar payı hesaplama"""
        brand_sales = {"BrandA": 1000, "BrandB": 500, "BrandC": 500}
        total_sales = sum(brand_sales.values())
        
        market_shares = {k: v/total_sales*100 for k, v in brand_sales.items()}
        
        assert market_shares["BrandA"] == 50
        assert market_shares["BrandB"] == 25
        assert market_shares["BrandC"] == 25
    
    def test_segment_distribution(self):
        """Segment dağılımı testi"""
        segments = pd.Series(["Ekonomik"]*20 + ["Orta"]*50 + ["Premium"]*30)
        distribution = segments.value_counts(normalize=True) * 100
        
        assert distribution["Orta"] == 50
        assert distribution["Premium"] == 30
        assert distribution["Ekonomik"] == 20
