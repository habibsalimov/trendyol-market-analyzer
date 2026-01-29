"""
Test modülü: Veri işleme fonksiyonları
"""
import pytest
import pandas as pd
import numpy as np
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestDataLoading:
    """Veri yükleme testleri"""
    
    def test_excel_file_exists(self):
        """Excel dosyalarının varlığını kontrol et"""
        outputs_dir = "outputs"
        assert os.path.exists(outputs_dir), "outputs/ klasörü bulunamadı"
        
        xlsx_files = [f for f in os.listdir(outputs_dir) if f.endswith('.xlsx')]
        assert len(xlsx_files) > 0, "Excel dosyası bulunamadı"
    
    def test_load_excel_data(self):
        """Excel verisi yükleme testi"""
        test_file = "outputs/output_CiltBakimi.xlsx"
        
        if os.path.exists(test_file):
            df = pd.read_excel(test_file)
            assert not df.empty, "DataFrame boş"
            assert len(df) > 0, "Veri satırı yok"
    
    def test_required_columns_exist(self):
        """Gerekli sütunların varlığını kontrol et"""
        test_file = "outputs/output_CiltBakimi.xlsx"
        required_columns = ["Ürün Adı", "Fiyat"]
        
        if os.path.exists(test_file):
            df = pd.read_excel(test_file)
            for col in required_columns:
                assert col in df.columns, f"'{col}' sütunu eksik"


class TestPriceCleaning:
    """Fiyat temizleme testleri"""
    
    def test_clean_price_numeric(self):
        """Sayısal fiyat temizleme"""
        def clean_price(price):
            if pd.isna(price):
                return None
            if isinstance(price, (int, float)):
                return float(price)
            try:
                # Turkish format: 1.299,90 -> 1299.90
                cleaned = str(price).replace("TL", "").replace(" ", "").strip()
                if "," in cleaned:
                    cleaned = cleaned.replace(".", "").replace(",", ".")
                return float(cleaned)
            except:
                return None
        
        assert clean_price(100) == 100.0
        assert clean_price(99.90) == 99.90
        assert clean_price("149,90") == 149.90  # Turkish decimal format
        assert clean_price(None) is None
    
    def test_clean_price_string(self):
        """String fiyat temizleme"""
        def clean_price(price):
            if pd.isna(price):
                return None
            if isinstance(price, (int, float)):
                return float(price)
            try:
                cleaned = str(price).replace("TL", "").replace(" ", "").strip()
                if "," in cleaned:
                    cleaned = cleaned.replace(".", "").replace(",", ".")
                return float(cleaned)
            except:
                return None
        
        assert clean_price("100 TL") == 100.0
        assert clean_price("1.299,90") == 1299.90  # Turkish format: 1.299,90 = 1299.90
    
    def test_price_statistics(self):
        """Fiyat istatistikleri hesaplama"""
        prices = pd.Series([100, 200, 300, 400, 500])
        
        assert prices.mean() == 300
        assert prices.median() == 300
        assert prices.min() == 100
        assert prices.max() == 500


class TestSegmentation:
    """Fiyat segmentasyon testleri"""
    
    def test_segment_calculation(self):
        """Segment hesaplama testi"""
        prices = pd.Series([50, 100, 150, 200, 250, 300, 350, 400])
        
        q1 = prices.quantile(0.25)
        median = prices.median()
        q3 = prices.quantile(0.75)
        
        def get_segment(price):
            if price <= q1:
                return "Ekonomik"
            elif price <= median:
                return "Orta-Alt"
            elif price <= q3:
                return "Orta-Üst"
            else:
                return "Premium"
        
        assert get_segment(50) == "Ekonomik"
        assert get_segment(150) == "Orta-Alt"
        assert get_segment(250) == "Orta-Üst"
        assert get_segment(400) == "Premium"
    
    def test_segment_distribution(self):
        """Segment dağılımı testi"""
        prices = pd.Series([100, 200, 300, 400] * 25)  # 100 ürün
        
        q1 = prices.quantile(0.25)
        median = prices.median()
        q3 = prices.quantile(0.75)
        
        ekonomik = len(prices[prices <= q1])
        premium = len(prices[prices > q3])
        
        assert ekonomik > 0
        assert premium > 0
        assert ekonomik + premium <= len(prices)


class TestDiscountAnalysis:
    """İndirim analizi testleri"""
    
    def test_discount_calculation(self):
        """İndirim oranı hesaplama"""
        original = 100
        current = 80
        discount = ((original - current) / original) * 100
        
        assert discount == 20.0
    
    def test_discount_with_dataframe(self):
        """DataFrame ile indirim hesaplama"""
        df = pd.DataFrame({
            "Fiyat": [80, 90, 100],
            "Orijinal Fiyat": [100, 100, 100]
        })
        
        df["Indirim"] = ((df["Orijinal Fiyat"] - df["Fiyat"]) / df["Orijinal Fiyat"] * 100)
        
        assert df["Indirim"].iloc[0] == 20.0
        assert df["Indirim"].iloc[1] == 10.0
        assert df["Indirim"].iloc[2] == 0.0


class TestBrandExtraction:
    """Marka çıkarma testleri"""
    
    def test_extract_brand_from_name(self):
        """Ürün adından marka çıkarma"""
        product_names = [
            "L'Oreal Paris Revitalift Krem",
            "Maybelline New York Fondöten",
            "Garnier Micellar Su"
        ]
        
        brands = [name.split()[0] for name in product_names]
        
        assert brands[0] == "L'Oreal"
        assert brands[1] == "Maybelline"
        assert brands[2] == "Garnier"
    
    def test_brand_grouping(self):
        """Marka gruplama testi"""
        df = pd.DataFrame({
            "Ürün Adı": ["Brand1 Ürün A", "Brand1 Ürün B", "Brand2 Ürün C"],
            "Fiyat": [100, 150, 200]
        })
        
        df["Marka"] = df["Ürün Adı"].apply(lambda x: x.split()[0])
        brand_counts = df["Marka"].value_counts()
        
        assert brand_counts["Brand1"] == 2
        assert brand_counts["Brand2"] == 1
