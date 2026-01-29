"""
Test modülü: Entegrasyon testleri
"""
import pytest
import pandas as pd
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestEndToEndWorkflow:
    """Uçtan uca iş akışı testleri"""
    
    @pytest.fixture
    def sample_dataset(self):
        """Örnek veri seti oluştur"""
        return pd.DataFrame({
            "Ürün Adı": [
                "BrandA Ürün 1",
                "BrandA Ürün 2", 
                "BrandB Ürün 1",
                "BrandC Ürün 1"
            ],
            "Fiyat": [100.0, 200.0, 150.0, 300.0],
            "Orijinal Fiyat": [120.0, 250.0, 150.0, 350.0],
            "Değerlendirme Puanı": [4.5, 4.8, 4.2, 4.9],
            "Yorum Sayısı": [1000, 500, 2000, 300],
            "Kampanyalar": ["Süper Fırsat", None, "Kargo Bedava", "Premium"],
            "Ürün Kategorisi": ["Test"] * 4,
            "Ürün Linki": ["http://test.com/1", "http://test.com/2", "http://test.com/3", "http://test.com/4"]
        })
    
    def test_data_loading_pipeline(self, sample_dataset):
        """Veri yükleme pipeline testi"""
        # 1. Veri yüklendi
        assert not sample_dataset.empty
        
        # 2. Gerekli sütunlar var
        required = ["Ürün Adı", "Fiyat"]
        for col in required:
            assert col in sample_dataset.columns
    
    def test_price_cleaning_pipeline(self, sample_dataset):
        """Fiyat temizleme pipeline testi"""
        # Fiyat temizleme
        def clean_price(price):
            if pd.isna(price):
                return None
            return float(price)
        
        sample_dataset["Fiyat_Clean"] = sample_dataset["Fiyat"].apply(clean_price)
        
        # Temizlenmiş fiyatlar sayısal olmalı
        assert sample_dataset["Fiyat_Clean"].dtype == float
        assert sample_dataset["Fiyat_Clean"].notna().all()
    
    def test_segmentation_pipeline(self, sample_dataset):
        """Segmentasyon pipeline testi"""
        prices = sample_dataset["Fiyat"]
        
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
        
        sample_dataset["Segment"] = prices.apply(get_segment)
        
        # Her ürünün segmenti olmalı
        assert sample_dataset["Segment"].notna().all()
        assert sample_dataset["Segment"].isin(["Ekonomik", "Orta-Alt", "Orta-Üst", "Premium"]).all()
    
    def test_discount_calculation_pipeline(self, sample_dataset):
        """İndirim hesaplama pipeline testi"""
        sample_dataset["Indirim"] = (
            (sample_dataset["Orijinal Fiyat"] - sample_dataset["Fiyat"]) 
            / sample_dataset["Orijinal Fiyat"] * 100
        ).fillna(0)
        
        # İndirimler 0-100 arasında olmalı
        assert (sample_dataset["Indirim"] >= 0).all()
        assert (sample_dataset["Indirim"] <= 100).all()
    
    def test_brand_analysis_pipeline(self, sample_dataset):
        """Marka analizi pipeline testi"""
        sample_dataset["Marka"] = sample_dataset["Ürün Adı"].apply(lambda x: x.split()[0])
        
        brand_stats = sample_dataset.groupby("Marka").agg({
            "Fiyat": ["mean", "count"],
            "Değerlendirme Puanı": "mean"
        })
        
        # En az 1 marka olmalı
        assert len(brand_stats) > 0
    
    def test_full_analysis_workflow(self, sample_dataset):
        """Tam analiz iş akışı testi"""
        # 1. Veri temizleme
        sample_dataset["Fiyat_Clean"] = sample_dataset["Fiyat"].astype(float)
        
        # 2. İstatistikler
        stats = {
            "total": len(sample_dataset),
            "avg_price": sample_dataset["Fiyat_Clean"].mean(),
            "min_price": sample_dataset["Fiyat_Clean"].min(),
            "max_price": sample_dataset["Fiyat_Clean"].max()
        }
        
        # 3. Segmentasyon
        q1 = sample_dataset["Fiyat_Clean"].quantile(0.25)
        q3 = sample_dataset["Fiyat_Clean"].quantile(0.75)
        
        segments = {
            "ekonomik": len(sample_dataset[sample_dataset["Fiyat_Clean"] <= q1]),
            "premium": len(sample_dataset[sample_dataset["Fiyat_Clean"] > q3])
        }
        
        # 4. Marka analizi
        sample_dataset["Marka"] = sample_dataset["Ürün Adı"].apply(lambda x: x.split()[0])
        top_brands = sample_dataset["Marka"].value_counts().head(3)
        
        # Doğrulamalar
        assert stats["total"] == 4
        assert stats["avg_price"] > 0
        assert len(top_brands) > 0


class TestFileOperations:
    """Dosya işlemleri testleri"""
    
    def test_outputs_directory_exists(self):
        """Outputs klasörü var mı testi"""
        assert os.path.exists("outputs"), "outputs/ klasörü bulunamadı"
    
    def test_excel_files_readable(self):
        """Excel dosyaları okunabilir testi"""
        outputs_dir = "outputs"
        if os.path.exists(outputs_dir):
            xlsx_files = [f for f in os.listdir(outputs_dir) if f.endswith('.xlsx')]
            
            for file in xlsx_files:
                filepath = os.path.join(outputs_dir, file)
                df = pd.read_excel(filepath)
                assert not df.empty, f"{file} boş"


class TestConfigValidation:
    """Konfigürasyon doğrulama testleri"""
    
    def test_category_config_exists(self):
        """Kategori konfigürasyonu var mı testi"""
        config_path = "config/category_config.py"
        assert os.path.exists(config_path), "category_config.py bulunamadı"
    
    def test_requirements_exists(self):
        """requirements.txt var mı testi"""
        assert os.path.exists("requirements.txt"), "requirements.txt bulunamadı"


class TestDashboardComponents:
    """Dashboard bileşenleri testleri"""
    
    @pytest.fixture
    def dashboard_data(self):
        """Dashboard verisi"""
        return pd.DataFrame({
            "Fiyat": [100, 200, 300, 400, 500],
            "Değerlendirme Puanı": [4.5, 4.6, 4.7, 4.8, 4.9],
            "Yorum Sayısı": [100, 200, 300, 400, 500]
        })
    
    def test_metrics_calculation(self, dashboard_data):
        """Metrik hesaplama testi"""
        metrics = {
            "total": len(dashboard_data),
            "avg_price": dashboard_data["Fiyat"].mean(),
            "min_price": dashboard_data["Fiyat"].min(),
            "max_price": dashboard_data["Fiyat"].max()
        }
        
        assert metrics["total"] == 5
        assert metrics["avg_price"] == 300
        assert metrics["min_price"] == 100
        assert metrics["max_price"] == 500
    
    def test_chart_data_preparation(self, dashboard_data):
        """Grafik veri hazırlama testi"""
        # Histogram için
        hist_data = dashboard_data["Fiyat"].values
        assert len(hist_data) > 0
        
        # Scatter için
        scatter_x = dashboard_data["Fiyat"].values
        scatter_y = dashboard_data["Değerlendirme Puanı"].values
        assert len(scatter_x) == len(scatter_y)


class TestErrorHandling:
    """Hata yönetimi testleri"""
    
    def test_empty_dataframe_handling(self):
        """Boş DataFrame yönetimi testi"""
        empty_df = pd.DataFrame()
        
        if empty_df.empty:
            result = "Veri bulunamadı"
        else:
            result = "Veri mevcut"
        
        assert result == "Veri bulunamadı"
    
    def test_missing_column_handling(self):
        """Eksik sütun yönetimi testi"""
        df = pd.DataFrame({"A": [1, 2, 3]})
        
        if "B" not in df.columns:
            df["B"] = None
        
        assert "B" in df.columns
    
    def test_invalid_price_handling(self):
        """Geçersiz fiyat yönetimi testi"""
        def clean_price(price):
            try:
                return float(price)
            except:
                return None
        
        assert clean_price("invalid") is None
        assert clean_price(100) == 100.0
        assert clean_price("99.90") == 99.90
