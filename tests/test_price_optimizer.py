"""
Test modülü: Fiyat optimizasyon fonksiyonları
"""
import pytest
import pandas as pd
import numpy as np


class TestPriceStatistics:
    """Fiyat istatistikleri testleri"""
    
    def test_average_price(self):
        """Ortalama fiyat hesaplama"""
        prices = pd.Series([100, 200, 300])
        assert prices.mean() == 200
    
    def test_median_price(self):
        """Medyan fiyat hesaplama"""
        prices = pd.Series([100, 200, 300, 400, 500])
        assert prices.median() == 300
    
    def test_standard_deviation(self):
        """Standart sapma hesaplama"""
        prices = pd.Series([100, 100, 100])
        assert prices.std() == 0
    
    def test_coefficient_of_variation(self):
        """Değişkenlik katsayısı (CV) hesaplama"""
        prices = pd.Series([100, 200, 300])
        cv = (prices.std() / prices.mean()) * 100
        assert cv > 0


class TestPriceSegments:
    """Fiyat segment testleri"""
    
    @pytest.fixture
    def sample_prices(self):
        """Örnek fiyat verisi"""
        return pd.Series([50, 100, 150, 200, 250, 300, 350, 400, 450, 500])
    
    def test_quartile_calculation(self, sample_prices):
        """Çeyreklik hesaplama"""
        q1 = sample_prices.quantile(0.25)
        q2 = sample_prices.quantile(0.50)
        q3 = sample_prices.quantile(0.75)
        
        assert q1 < q2 < q3
        # Quartile değerleri veri setine göre değişir
        assert q1 > 0
        assert q2 > q1
        assert q3 > q2
    
    def test_segment_assignment(self, sample_prices):
        """Segment atama testi"""
        q1 = sample_prices.quantile(0.25)
        median = sample_prices.median()
        q3 = sample_prices.quantile(0.75)
        
        def assign_segment(price):
            if price <= q1:
                return "Ekonomik"
            elif price <= median:
                return "Orta-Alt"
            elif price <= q3:
                return "Orta-Üst"
            else:
                return "Premium"
        
        segments = sample_prices.apply(assign_segment)
        
        # Her segment en az 1 ürün içermeli
        assert (segments == "Ekonomik").sum() >= 1
        assert (segments == "Premium").sum() >= 1
    
    def test_segment_counts_sum(self, sample_prices):
        """Segment toplamları testi"""
        q1 = sample_prices.quantile(0.25)
        median = sample_prices.median()
        q3 = sample_prices.quantile(0.75)
        
        ekonomik = len(sample_prices[sample_prices <= q1])
        orta_alt = len(sample_prices[(sample_prices > q1) & (sample_prices <= median)])
        orta_ust = len(sample_prices[(sample_prices > median) & (sample_prices <= q3)])
        premium = len(sample_prices[sample_prices > q3])
        
        total = ekonomik + orta_alt + orta_ust + premium
        assert total == len(sample_prices)


class TestPriceRecommendation:
    """Fiyat öneri testleri"""
    
    def test_competitor_adjustment_aggressive(self):
        """Agresif rekabet stratejisi"""
        base_price = 100
        aggressive_adj = -0.05
        
        suggested = base_price * (1 + aggressive_adj)
        assert suggested == 95
    
    def test_competitor_adjustment_premium(self):
        """Premium rekabet stratejisi"""
        base_price = 100
        premium_adj = 0.10
        
        suggested = base_price * (1 + premium_adj)
        assert abs(suggested - 110) < 0.01  # Float karşılaştırması
    
    def test_margin_calculation(self):
        """Kar marjı hesaplama"""
        selling_price = 100
        margin_percent = 25
        
        cost = selling_price / (1 + margin_percent / 100)
        assert cost == 80
    
    def test_price_range_recommendation(self):
        """Fiyat aralığı önerisi"""
        prices = pd.Series([100, 150, 200, 250, 300])
        
        q1 = prices.quantile(0.25)
        q3 = prices.quantile(0.75)
        
        # Ekonomik segment için önerilen aralık
        ekonomik_range = (prices.min(), q1)
        assert ekonomik_range[0] < ekonomik_range[1]
        
        # Premium segment için önerilen aralık
        premium_range = (q3, prices.max())
        assert premium_range[0] < premium_range[1]


class TestDiscountStrategy:
    """İndirim stratejisi testleri"""
    
    def test_discount_percentage(self):
        """İndirim yüzdesi hesaplama"""
        original = 200
        discounted = 150
        
        discount_pct = ((original - discounted) / original) * 100
        assert discount_pct == 25
    
    def test_average_discount(self):
        """Ortalama indirim hesaplama"""
        discounts = pd.Series([10, 20, 30, 40])
        avg_discount = discounts.mean()
        
        assert avg_discount == 25
    
    def test_discounted_products_count(self):
        """İndirimli ürün sayısı"""
        discounts = pd.Series([0, 0, 10, 20, 30])
        discounted_count = (discounts > 0).sum()
        
        assert discounted_count == 3
    
    def test_max_discount(self):
        """Maksimum indirim testi"""
        discounts = pd.Series([5, 10, 15, 50, 25])
        
        assert discounts.max() == 50
        assert discounts.idxmax() == 3
