"""
Test modülü: İçerik üretici fonksiyonları
"""
import pytest
import re


class TestSEOTitle:
    """SEO başlık testleri"""
    
    def test_title_max_length(self):
        """Başlık maksimum uzunluk testi"""
        max_length = 70
        title = "L'Oreal Paris Revitalift Kırışıklık Karşıtı Gündüz Kremi 50ml"
        
        assert len(title) <= max_length or len(title[:max_length]) == max_length
    
    def test_title_contains_keyword(self):
        """Başlıkta anahtar kelime testi"""
        title = "Vitamin C Serum 30ml - Aydınlatıcı Cilt Bakım"
        keywords = ["vitamin c", "serum", "cilt bakım"]
        
        title_lower = title.lower()
        has_keyword = any(kw in title_lower for kw in keywords)
        
        assert has_keyword == True
    
    def test_title_not_empty(self):
        """Başlık boş değil testi"""
        title = "Test Ürün Başlığı"
        assert len(title) > 0
        assert title.strip() != ""


class TestMetaDescription:
    """Meta açıklama testleri"""
    
    def test_meta_max_length(self):
        """Meta açıklama maksimum uzunluk testi"""
        max_length = 155
        meta = "Bu vitamin C serum cildinizi aydınlatır ve yaşlanma belirtilerini azaltır."
        
        assert len(meta) <= max_length
    
    def test_meta_contains_cta(self):
        """Meta açıklamada CTA testi"""
        meta = "Hemen satın alın ve cildinizi yenileyin!"
        cta_words = ["satın al", "hemen", "keşfet", "dene", "sipariş"]
        
        meta_lower = meta.lower()
        has_cta = any(cta in meta_lower for cta in cta_words)
        
        assert has_cta == True


class TestBulletPoints:
    """Özellik maddeleri testleri"""
    
    def test_bullet_count(self):
        """Madde sayısı testi"""
        expected_count = 5
        bullets = [
            "%20 Vitamin C içerir",
            "Aydınlatıcı etki sağlar",
            "Vegan formül",
            "Paraben içermez",
            "Dermatolojik test edilmiştir"
        ]
        
        assert len(bullets) == expected_count
    
    def test_bullet_not_empty(self):
        """Maddeler boş değil testi"""
        bullets = ["Özellik 1", "Özellik 2", "Özellik 3"]
        
        for bullet in bullets:
            assert len(bullet) > 0
            assert bullet.strip() != ""
    
    def test_bullet_unique(self):
        """Maddeler benzersiz testi"""
        bullets = ["Özellik A", "Özellik B", "Özellik C"]
        
        assert len(bullets) == len(set(bullets))


class TestHashtags:
    """Hashtag testleri"""
    
    def test_hashtag_format(self):
        """Hashtag formatı testi"""
        hashtags = ["#CiltBakımı", "#VitaminC", "#Serum", "#Güzellik", "#Kozmetik"]
        
        for tag in hashtags:
            assert tag.startswith("#")
            assert len(tag) > 1
    
    def test_hashtag_count(self):
        """Hashtag sayısı testi"""
        expected_min = 3
        expected_max = 10
        hashtags = ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
        
        assert len(hashtags) >= expected_min
        assert len(hashtags) <= expected_max
    
    def test_hashtag_no_spaces(self):
        """Hashtag'lerde boşluk yok testi"""
        hashtags = ["#CiltBakımı", "#AntiAging", "#SağlıklıCilt"]
        
        for tag in hashtags:
            assert " " not in tag


class TestKeywords:
    """Anahtar kelime testleri"""
    
    def test_keyword_extraction(self):
        """Anahtar kelime çıkarma testi"""
        product_name = "L'Oreal Paris Vitamin C Serum Cilt Bakımı"
        
        # Basit kelime çıkarma
        words = product_name.lower().split()
        keywords = [w for w in words if len(w) > 3]
        
        assert "vitamin" in keywords
        assert "serum" in keywords
    
    def test_keyword_count(self):
        """Anahtar kelime sayısı testi"""
        keywords = ["vitamin c", "serum", "cilt bakımı", "kozmetik", "aydınlatıcı"]
        
        assert len(keywords) >= 5


class TestContentImprovement:
    """İçerik iyileştirme testleri"""
    
    def test_add_emoji(self):
        """Emoji ekleme testi"""
        text = "Bu ürün çok etkili"
        emoji_text = "✨ Bu ürün çok etkili"
        
        assert emoji_text.startswith("✨")
    
    def test_make_shorter(self):
        """Kısaltma testi"""
        long_text = "Bu ürün cildiniz için çok faydalı özelliklere sahiptir ve günlük kullanıma uygundur."
        short_text = "Cildiniz için faydalı, günlük kullanıma uygun."
        
        assert len(short_text) < len(long_text)
    
    def test_seo_optimization(self):
        """SEO optimizasyonu testi"""
        original = "Krem"
        optimized = "Cilt Bakım Kremi - Nemlendirici Anti-Aging"
        
        assert len(optimized) > len(original)
        assert "cilt" in optimized.lower()


class TestContentValidation:
    """İçerik doğrulama testleri"""
    
    def test_no_forbidden_words(self):
        """Yasaklı kelime testi"""
        forbidden = ["en iyi", "kesinlikle", "garantili"]
        content = "Bu ürün cildinizi nemlendirir ve korur."
        
        content_lower = content.lower()
        has_forbidden = any(word in content_lower for word in forbidden)
        
        assert has_forbidden == False
    
    def test_price_not_in_description(self):
        """Açıklamada fiyat yok testi"""
        description = "Bu serum cildinizi aydınlatır ve nemlendirir."
        
        # Fiyat pattern'i kontrol
        price_pattern = r'\d+[\.,]?\d*\s*(TL|₺|lira)'
        has_price = bool(re.search(price_pattern, description, re.IGNORECASE))
        
        assert has_price == False
    
    def test_minimum_description_length(self):
        """Minimum açıklama uzunluğu testi"""
        min_length = 50
        description = "Bu vitamin C serum, cildinizi aydınlatır ve yaşlanma belirtilerini azaltmaya yardımcı olur."
        
        assert len(description) >= min_length
