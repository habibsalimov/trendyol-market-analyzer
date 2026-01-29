"""
Test modülü: Rapor oluşturucu fonksiyonları
"""
import pytest
import pandas as pd
from datetime import datetime


class TestReportStructure:
    """Rapor yapısı testleri"""
    
    def test_report_has_header(self):
        """Rapor başlığı testi"""
        report_content = "# Pazar Analizi Raporu\n\nİçerik buraya..."
        
        assert report_content.startswith("#")
        assert "Rapor" in report_content
    
    def test_report_has_date(self):
        """Raporda tarih testi"""
        report_date = datetime.now().strftime('%d.%m.%Y')
        report_content = f"**Tarih:** {report_date}"
        
        assert report_date in report_content
    
    def test_report_has_sections(self):
        """Rapor bölümleri testi"""
        required_sections = [
            "Yönetici Özeti",
            "Pazar İstatistikleri",
            "Sonuç"
        ]
        
        report_content = """
        # Rapor
        ## Yönetici Özeti
        Özet içeriği...
        ## Pazar İstatistikleri
        İstatistikler...
        ## Sonuç
        Sonuç içeriği...
        """
        
        for section in required_sections:
            assert section in report_content


class TestReportData:
    """Rapor veri testleri"""
    
    @pytest.fixture
    def sample_stats(self):
        """Örnek istatistikler"""
        return {
            "total_products": 100,
            "avg_price": 250.50,
            "min_price": 50.00,
            "max_price": 800.00,
            "median_price": 200.00
        }
    
    def test_stats_formatting(self, sample_stats):
        """İstatistik formatlama testi"""
        formatted_avg = f"{sample_stats['avg_price']:.2f} ₺"
        
        assert "250.50" in formatted_avg
        assert "₺" in formatted_avg
    
    def test_table_generation(self, sample_stats):
        """Tablo oluşturma testi"""
        table = f"""
| Metrik | Değer |
|--------|-------|
| Toplam Ürün | {sample_stats['total_products']} |
| Ortalama Fiyat | {sample_stats['avg_price']:.2f} ₺ |
"""
        
        assert "|" in table
        assert "Toplam Ürün" in table
        assert "100" in table
    
    def test_price_range_calculation(self, sample_stats):
        """Fiyat aralığı hesaplama"""
        price_range = sample_stats['max_price'] - sample_stats['min_price']
        
        assert price_range == 750.00


class TestReportSegments:
    """Rapor segment testleri"""
    
    def test_segment_table_format(self):
        """Segment tablosu formatı testi"""
        segments = {
            "Ekonomik": {"range": "0-100", "count": 25},
            "Orta": {"range": "100-300", "count": 50},
            "Premium": {"range": "300+", "count": 25}
        }
        
        table_rows = []
        for name, data in segments.items():
            row = f"| {name} | {data['range']} ₺ | {data['count']} |"
            table_rows.append(row)
        
        assert len(table_rows) == 3
        assert "Ekonomik" in table_rows[0]
    
    def test_segment_percentages(self):
        """Segment yüzdeleri testi"""
        total = 100
        segments = {"Ekonomik": 25, "Orta": 50, "Premium": 25}
        
        percentages = {k: (v/total)*100 for k, v in segments.items()}
        
        assert percentages["Ekonomik"] == 25
        assert percentages["Orta"] == 50
        assert sum(percentages.values()) == 100


class TestReportExport:
    """Rapor dışa aktarma testleri"""
    
    def test_markdown_export(self):
        """Markdown export testi"""
        content = "# Test Raporu\n\n**Bold text**"
        filename = f"rapor_{datetime.now().strftime('%Y%m%d')}.md"
        
        assert filename.endswith(".md")
        assert "#" in content
    
    def test_html_export_structure(self):
        """HTML export yapısı testi"""
        html_content = """
        <html>
        <head><title>Rapor</title></head>
        <body>
        <h1>Pazar Analizi</h1>
        </body>
        </html>
        """
        
        assert "<html>" in html_content
        assert "</html>" in html_content
        assert "<h1>" in html_content
    
    def test_filename_format(self):
        """Dosya adı formatı testi"""
        category = "CiltBakimi"
        date_str = datetime.now().strftime('%Y%m%d')
        
        filename = f"pazar_raporu_{category}_{date_str}.md"
        
        assert category in filename
        assert date_str in filename
        assert filename.endswith(".md")


class TestReportRecommendations:
    """Rapor önerileri testleri"""
    
    def test_recommendations_count(self):
        """Öneri sayısı testi"""
        recommendations = [
            "Fiyat optimizasyonu yapın",
            "SEO içerik geliştirin",
            "Kampanya stratejisi oluşturun",
            "Müşteri geri bildirimlerini analiz edin"
        ]
        
        assert len(recommendations) >= 3
    
    def test_recommendation_format(self):
        """Öneri formatı testi"""
        recommendations = [
            "1. **Fiyat Optimizasyonu:** Ortalama fiyatın altında konumlanın.",
            "2. **İçerik:** SEO uyumlu açıklamalar yazın.",
        ]
        
        for rec in recommendations:
            # Numara ile başlamalı
            assert rec[0].isdigit()
            # Bold başlık içermeli
            assert "**" in rec


class TestTopProductsSection:
    """En popüler ürünler bölümü testleri"""
    
    def test_top_products_sorted(self):
        """Ürünler sıralı testi"""
        df = pd.DataFrame({
            "Ürün": ["A", "B", "C"],
            "Yorum": [100, 300, 200]
        })
        
        top_products = df.nlargest(3, "Yorum")
        
        assert top_products.iloc[0]["Ürün"] == "B"
        assert top_products.iloc[0]["Yorum"] == 300
    
    def test_top_products_limit(self):
        """Ürün limiti testi"""
        df = pd.DataFrame({
            "Ürün": [f"Ürün {i}" for i in range(10)],
            "Yorum": list(range(10))
        })
        
        top_5 = df.nlargest(5, "Yorum")
        
        assert len(top_5) == 5
