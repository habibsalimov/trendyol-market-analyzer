import streamlit as st
import pandas as pd
import numpy as np
import os
import glob
import io
from datetime import datetime
from src.analysis.gemini_analyzer import GeminiAnalyzer
from dotenv import load_dotenv
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables for API key
load_dotenv()

st.set_page_config(page_title="Trendyol Market Analyzer", page_icon="📊", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #FF6B35 0%, #F7931E 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    .sub-header {
        color: #666;
        font-size: 1.1rem;
        margin-top: 0;
    }
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 12px;
        border-left: 4px solid #667eea;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 10px;
        padding: 15px;
        color: #155724;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 10px;
        padding: 15px;
        color: #856404;
    }
    .info-card {
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">📊 Trendyol Pazar Analizi</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Yapay Zeka Destekli Satış Optimizasyon Sistemi | ESEY Kozmetik | BTÜ-İMEP 2025</p>', unsafe_allow_html=True)

# Sidebar
st.sidebar.image("https://cdn.worldvectorlogo.com/logos/trendyol-1.svg", width=150)
st.sidebar.markdown("---")

page = st.sidebar.radio("🧭 Modül Seçimi", [
    "📊 Dashboard", 
    "📋 AI Analiz Raporu", 
    "💰 Fiyat Optimizasyonu",
    "📈 Rakip Analizi",
    "✍️ İçerik Üretici",
    "💬 AI Asistanı",
    "📄 Rapor Oluştur"
])

# Category Selection
st.sidebar.markdown("---")
st.sidebar.header("📁 Veri Kaynağı")
output_files = glob.glob("outputs/output_*.xlsx")
categories = [f.split("output_")[-1].replace(".xlsx", "") for f in output_files]

if not categories:
    st.sidebar.error("⚠️ Veri bulunamadı!")
    st.info("Demo modu için outputs/ klasörüne Excel dosyası ekleyin.")
    st.stop()

selected_category = st.sidebar.selectbox("Kategori", categories, format_func=lambda x: f"📦 {x}")
file_path = f"outputs/output_{selected_category}.xlsx"

# Sidebar Info
st.sidebar.markdown("---")
st.sidebar.markdown("**📊 Proje Bilgileri**")
st.sidebar.markdown("""
- 🎓 BTÜ-İMEP Projesi
- 👤 Habib Salim
- 🏢 ESEY Kozmetik
- 📅 2025-2026
""")

# Load data
@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(file_path)

# Clean price data
def clean_price(price):
    if pd.isna(price):
        return None
    if isinstance(price, (int, float)):
        return float(price)
    try:
        return float(str(price).replace("TL", "").replace(".", "").replace(",", ".").strip())
    except:
        return None

df["Fiyat_Clean"] = df["Fiyat"].apply(clean_price)
df["Orijinal_Fiyat_Clean"] = df.get("Orijinal Fiyat", pd.Series([None]*len(df))).apply(clean_price)

# Clean review count
if "Yorum Sayısı" in df.columns:
    df["Yorum_Clean"] = pd.to_numeric(df["Yorum Sayısı"], errors="coerce")

# Calculate discount
if df["Orijinal_Fiyat_Clean"].notna().any():
    df["Indirim_Orani"] = ((df["Orijinal_Fiyat_Clean"] - df["Fiyat_Clean"]) / df["Orijinal_Fiyat_Clean"] * 100).fillna(0)
else:
    df["Indirim_Orani"] = 0

# Session state init
if "current_category" not in st.session_state:
    st.session_state.current_category = None

if st.session_state.current_category != selected_category:
    st.session_state.chat_session = None
    st.session_state.chat_history = []
    st.session_state.analysis_report = None
    st.session_state.current_category = selected_category
    st.session_state.messages = []

# ============================================
# PAGE 1: DASHBOARD
# ============================================
if page == "📊 Dashboard":
    st.subheader(f"📊 {selected_category} - Pazar Özeti")
    
    # Key Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    
    avg_price = df["Fiyat_Clean"].mean()
    min_price = df["Fiyat_Clean"].min()
    max_price = df["Fiyat_Clean"].max()
    total_products = len(df)
    avg_discount = df[df["Indirim_Orani"] > 0]["Indirim_Orani"].mean() if (df["Indirim_Orani"] > 0).any() else 0
    
    with col1:
        st.metric("📦 Toplam Ürün", f"{total_products}")
    with col2:
        st.metric("💰 Ort. Fiyat", f"{avg_price:.0f} ₺")
    with col3:
        st.metric("📉 Min Fiyat", f"{min_price:.0f} ₺")
    with col4:
        st.metric("📈 Max Fiyat", f"{max_price:.0f} ₺")
    with col5:
        st.metric("🏷️ Ort. İndirim", f"%{avg_discount:.1f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Fiyat Dağılımı")
        fig = px.histogram(df, x="Fiyat_Clean", nbins=15, 
                          labels={"Fiyat_Clean": "Fiyat (₺)", "count": "Ürün Sayısı"},
                          color_discrete_sequence=["#667eea"])
        fig.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### ⭐ Değerlendirme vs Fiyat")
        if "Değerlendirme Puanı" in df.columns:
            df_plot = df.dropna(subset=["Fiyat_Clean", "Değerlendirme Puanı"])
            fig2 = px.scatter(df_plot, x="Fiyat_Clean", y="Değerlendirme Puanı",
                             size="Yorum_Clean" if "Yorum_Clean" in df.columns else None,
                             hover_name="Ürün Adı",
                             labels={"Fiyat_Clean": "Fiyat (₺)", "Değerlendirme Puanı": "Puan"},
                             color_discrete_sequence=["#764ba2"])
            fig2.update_layout(height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("Değerlendirme verisi yok.")
    
    # Charts Row 2
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏷️ Kampanya Dağılımı")
        if "Kampanyalar" in df.columns:
            campaign_counts = df["Kampanyalar"].fillna("Kampanyasız").value_counts()
            fig3 = px.pie(values=campaign_counts.values, names=campaign_counts.index,
                         color_discrete_sequence=px.colors.qualitative.Set3)
            fig3.update_layout(height=300, margin=dict(t=20, b=20))
            st.plotly_chart(fig3, use_container_width=True)
        else:
            st.info("Kampanya verisi yok.")
    
    with col2:
        st.markdown("#### 📈 Fiyat Segmentleri")
        q1 = df["Fiyat_Clean"].quantile(0.25)
        median = df["Fiyat_Clean"].median()
        q3 = df["Fiyat_Clean"].quantile(0.75)
        
        def get_segment(price):
            if price <= q1: return "🟢 Ekonomik"
            elif price <= median: return "🔵 Orta-Alt"
            elif price <= q3: return "🟡 Orta-Üst"
            else: return "🔴 Premium"
        
        df["Segment"] = df["Fiyat_Clean"].apply(get_segment)
        segment_counts = df["Segment"].value_counts()
        
        fig4 = px.bar(x=segment_counts.index, y=segment_counts.values,
                     labels={"x": "Segment", "y": "Ürün Sayısı"},
                     color=segment_counts.index,
                     color_discrete_map={"🟢 Ekonomik": "#2ecc71", "🔵 Orta-Alt": "#3498db", 
                                        "🟡 Orta-Üst": "#f1c40f", "🔴 Premium": "#e74c3c"})
        fig4.update_layout(showlegend=False, height=300, margin=dict(t=20, b=20))
        st.plotly_chart(fig4, use_container_width=True)
    
    # Top Products Table
    st.markdown("---")
    st.markdown("#### 🏆 En Popüler Ürünler")
    
    if "Yorum_Clean" in df.columns:
        top_products = df.nlargest(5, "Yorum_Clean")[["Ürün Adı", "Fiyat", "Değerlendirme Puanı", "Yorum Sayısı", "Kampanyalar"]]
        st.dataframe(top_products, use_container_width=True, hide_index=True)
    else:
        st.dataframe(df.head(5)[["Ürün Adı", "Fiyat"]], use_container_width=True, hide_index=True)
    
    # Export
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False, engine='openpyxl')
        st.download_button(
            label="📥 Excel İndir",
            data=buffer.getvalue(),
            file_name=f"trendyol_{selected_category}_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ============================================
# PAGE 2: AI ANALYSIS REPORT
# ============================================
elif page == "📋 AI Analiz Raporu":
    st.subheader(f"📋 {selected_category} - AI Analiz Raporu")
    
    report_cache_path = f"outputs/analysis_{selected_category}_report.md"
    
    if st.session_state.analysis_report is None and os.path.exists(report_cache_path):
        with open(report_cache_path, "r", encoding="utf-8") as f:
            st.session_state.analysis_report = f.read()
            st.success("💾 Önceki analiz yüklendi.")

    col1, col2 = st.columns([1, 3])
    with col1:
        button_label = "🚀 AI Analizi Başlat" if not st.session_state.analysis_report else "🔄 Yenile"
        run_analysis = st.button(button_label, type="primary", use_container_width=True)
    
    if run_analysis:
        with st.spinner("🤖 Gemini AI analiz ediyor... (30-60 sn)"):
            try:
                analyzer = GeminiAnalyzer()
                report = analyzer.analyze_category(file_path)
                st.session_state.analysis_report = report
                
                with open(report_cache_path, "w", encoding="utf-8") as f:
                    f.write(report)
                
                st.session_state.chat_session = analyzer.create_chat_session(df)
                st.success("✅ Analiz Tamamlandı!")
                st.rerun()
            except Exception as e:
                st.error(f"Hata: {str(e)}")

    if st.session_state.get("analysis_report"):
        st.markdown("---")
        st.markdown(st.session_state.analysis_report)

# ============================================
# PAGE 3: PRICE OPTIMIZATION
# ============================================
elif page == "💰 Fiyat Optimizasyonu":
    st.subheader(f"💰 {selected_category} - Fiyat Optimizasyonu")
    
    st.markdown("""
    > 🎯 **Amaç:** Rakip fiyatlarını analiz ederek pazar konumlandırması ve optimal fiyat önerileri sunmak.
    """)
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    avg_price = df["Fiyat_Clean"].mean()
    median_price = df["Fiyat_Clean"].median()
    std_price = df["Fiyat_Clean"].std()
    cv = (std_price / avg_price) * 100  # Coefficient of variation
    
    with col1:
        st.metric("📊 Ortalama", f"{avg_price:.0f} ₺")
    with col2:
        st.metric("📊 Medyan", f"{median_price:.0f} ₺")
    with col3:
        st.metric("📊 Std Sapma", f"{std_price:.0f} ₺")
    with col4:
        st.metric("📊 Değişkenlik", f"%{cv:.1f}")
    
    st.markdown("---")
    
    # Price Distribution with Stats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Fiyat Box Plot")
        fig = go.Figure()
        fig.add_trace(go.Box(y=df["Fiyat_Clean"], name="Fiyat", 
                            boxpoints='outliers', marker_color='#667eea'))
        fig.update_layout(height=350, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Segment Dağılımı")
        q1 = df["Fiyat_Clean"].quantile(0.25)
        q3 = df["Fiyat_Clean"].quantile(0.75)
        
        segments = {
            "🟢 Ekonomik": len(df[df["Fiyat_Clean"] <= q1]),
            "🔵 Orta-Alt": len(df[(df["Fiyat_Clean"] > q1) & (df["Fiyat_Clean"] <= median_price)]),
            "🟡 Orta-Üst": len(df[(df["Fiyat_Clean"] > median_price) & (df["Fiyat_Clean"] <= q3)]),
            "🔴 Premium": len(df[df["Fiyat_Clean"] > q3])
        }
        
        fig2 = px.pie(values=list(segments.values()), names=list(segments.keys()),
                     color_discrete_sequence=["#2ecc71", "#3498db", "#f1c40f", "#e74c3c"])
        fig2.update_layout(height=350, margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)
    
    # Price Optimizer Tool
    st.markdown("---")
    st.markdown("#### 🎯 Fiyat Öneri Aracı")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        target_segment = st.selectbox("Hedef Segment", ["Ekonomik", "Orta", "Premium"])
    with col2:
        margin = st.slider("Kar Marjı (%)", 10, 60, 30)
    with col3:
        competition = st.selectbox("Rekabet Stratejisi", ["Agresif (-5%)", "Nötr", "Premium (+10%)"])
    
    # Calculate suggested price
    comp_adj = -0.05 if "Agresif" in competition else (0.10 if "Premium" in competition else 0)
    
    if target_segment == "Ekonomik":
        base_price = q1
        range_low = min_price
        range_high = q1
    elif target_segment == "Orta":
        base_price = median_price
        range_low = q1
        range_high = q3
    else:
        base_price = q3 * 1.1
        range_low = q3
        range_high = max_price
    
    suggested = base_price * (1 + comp_adj)
    cost_estimate = suggested / (1 + margin/100)
    
    st.markdown("---")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.success(f"💡 **Önerilen Fiyat:** {suggested:.0f} ₺")
    with col2:
        st.info(f"📊 **Fiyat Aralığı:** {range_low:.0f} - {range_high:.0f} ₺")
    with col3:
        st.warning(f"💵 **Tahmini Maliyet:** {cost_estimate:.0f} ₺")
    
    # Discount Analysis
    st.markdown("---")
    st.markdown("#### 🏷️ İndirim Stratejisi Analizi")
    
    col1, col2 = st.columns(2)
    
    with col1:
        discounted = df[df["Indirim_Orani"] > 0]
        if len(discounted) > 0:
            avg_disc = discounted["Indirim_Orani"].mean()
            max_disc = discounted["Indirim_Orani"].max()
            st.metric("📉 Ort. İndirim", f"%{avg_disc:.1f}")
            st.metric("📉 Max İndirim", f"%{max_disc:.1f}")
            st.metric("🏷️ İndirimli Ürün", f"{len(discounted)} / {len(df)}")
        else:
            st.info("İndirim verisi yok.")
    
    with col2:
        if len(discounted) > 0:
            fig = px.histogram(discounted, x="Indirim_Orani", nbins=10,
                              labels={"Indirim_Orani": "İndirim Oranı (%)", "count": "Ürün"},
                              color_discrete_sequence=["#e74c3c"])
            fig.update_layout(height=250, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

# ============================================
# PAGE 4: COMPETITOR ANALYSIS
# ============================================
elif page == "📈 Rakip Analizi":
    st.subheader(f"📈 {selected_category} - Rakip Analizi")
    
    st.markdown("""
    > 🔍 **Amaç:** Pazardaki rakipleri analiz ederek rekabet avantajı stratejileri geliştirmek.
    """)
    
    # Brand Analysis (extract from product names)
    st.markdown("#### 🏢 Marka Analizi")
    
    # Extract brand (first word usually)
    df["Marka"] = df["Ürün Adı"].apply(lambda x: str(x).split()[0] if pd.notna(x) else "Bilinmiyor")
    brand_stats = df.groupby("Marka").agg({
        "Fiyat_Clean": ["mean", "min", "max", "count"],
        "Değerlendirme Puanı": "mean" if "Değerlendirme Puanı" in df.columns else "count"
    }).round(2)
    brand_stats.columns = ["Ort. Fiyat", "Min Fiyat", "Max Fiyat", "Ürün Sayısı", "Ort. Puan"]
    brand_stats = brand_stats.sort_values("Ürün Sayısı", ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Top 10 Marka**")
        st.dataframe(brand_stats, use_container_width=True)
    
    with col2:
        fig = px.bar(x=brand_stats.index, y=brand_stats["Ürün Sayısı"],
                    labels={"x": "Marka", "y": "Ürün Sayısı"},
                    color=brand_stats["Ort. Fiyat"],
                    color_continuous_scale="Viridis")
        fig.update_layout(height=350, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    
    # Price Positioning Map
    st.markdown("---")
    st.markdown("#### 🗺️ Fiyat-Kalite Konumlandırma Haritası")
    
    if "Değerlendirme Puanı" in df.columns:
        fig = px.scatter(df, x="Fiyat_Clean", y="Değerlendirme Puanı",
                        size="Yorum_Clean" if "Yorum_Clean" in df.columns else None,
                        color="Marka",
                        hover_name="Ürün Adı",
                        labels={"Fiyat_Clean": "Fiyat (₺)", "Değerlendirme Puanı": "Değerlendirme"},
                        height=500)
        
        # Add quadrant lines
        fig.add_hline(y=df["Değerlendirme Puanı"].median(), line_dash="dash", line_color="gray")
        fig.add_vline(x=df["Fiyat_Clean"].median(), line_dash="dash", line_color="gray")
        
        # Add quadrant labels
        fig.add_annotation(x=df["Fiyat_Clean"].max()*0.9, y=df["Değerlendirme Puanı"].max()*0.98,
                          text="⭐ Premium Kalite", showarrow=False, font=dict(size=12, color="green"))
        fig.add_annotation(x=df["Fiyat_Clean"].min()*1.1, y=df["Değerlendirme Puanı"].max()*0.98,
                          text="💎 En İyi Değer", showarrow=False, font=dict(size=12, color="blue"))
        fig.add_annotation(x=df["Fiyat_Clean"].max()*0.9, y=df["Değerlendirme Puanı"].min()*1.02,
                          text="⚠️ Pahalı-Düşük", showarrow=False, font=dict(size=12, color="red"))
        fig.add_annotation(x=df["Fiyat_Clean"].min()*1.1, y=df["Değerlendirme Puanı"].min()*1.02,
                          text="🔄 Ekonomik", showarrow=False, font=dict(size=12, color="orange"))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Değerlendirme verisi gerekli.")
    
    # SWOT Summary
    st.markdown("---")
    st.markdown("#### 📋 Pazar SWOT Özeti")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💪 Güçlü Yönler**
        - Geniş ürün yelpazesi
        - Rekabetçi fiyat aralığı
        - Yüksek müşteri değerlendirmeleri
        
        **⚠️ Zayıf Yönler**
        - Yüksek rekabet
        - Fiyat baskısı
        - Marka farklılaşması zorluğu
        """)
    
    with col2:
        st.markdown("""
        **🚀 Fırsatlar**
        - Niş segment penetrasyonu
        - Premium segment boşluğu
        - Cross-sell potansiyeli
        
        **🔥 Tehditler**
        - Agresif indirim savaşları
        - Yeni rakip girişleri
        - Müşteri sadakati düşük
        """)

# ============================================
# PAGE 5: CONTENT GENERATOR
# ============================================
elif page == "✍️ İçerik Üretici":
    st.subheader("✍️ AI Destekli Ürün İçerik Üretici")
    
    st.markdown("""
    > 🤖 **NLP Tabanlı İçerik Üretimi:** SEO uyumlu, satış odaklı ürün açıklamaları üretin.
    """)
    
    tab1, tab2 = st.tabs(["📝 Yeni İçerik Üret", "🔄 Mevcut Ürünü İyileştir"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            product_name = st.text_input("📦 Ürün Adı", placeholder="Örn: Vitamin C Serum 30ml")
            product_category = st.selectbox("📁 Kategori", ["Cilt Bakımı", "Makyaj", "Saç Bakımı", "Parfüm", "Kişisel Bakım"])
            product_price = st.number_input("💰 Fiyat (₺)", min_value=0.0, value=149.90)
        
        with col2:
            key_features = st.text_area("✨ Öne Çıkan Özellikler", placeholder="Her satıra bir özellik:\n- %20 Vitamin C\n- Aydınlatıcı etki", height=100)
            target_audience = st.selectbox("👥 Hedef Kitle", ["Genel", "Genç (18-25)", "Yetişkin (25-40)", "Olgun (40+)"])
            tone = st.selectbox("🎨 Ton", ["Profesyonel", "Samimi", "Lüks/Premium", "Genç/Dinamik"])
        
        if st.button("🚀 İçerik Üret", type="primary"):
            if product_name:
                with st.spinner("🤖 AI içerik üretiyor..."):
                    try:
                        analyzer = GeminiAnalyzer()
                        
                        prompt = f"""
                        Trendyol için profesyonel bir ürün açıklaması yaz.
                        
                        Ürün: {product_name}
                        Kategori: {product_category}
                        Fiyat: {product_price} TL
                        Özellikler: {key_features}
                        Hedef Kitle: {target_audience}
                        Ton: {tone}
                        
                        Şunları üret:
                        
                        ## 1. SEO Başlık (max 70 karakter)
                        
                        ## 2. Kısa Açıklama (2-3 cümle)
                        
                        ## 3. Detaylı Açıklama (3 paragraf)
                        
                        ## 4. Öne Çıkan Özellikler (5 bullet point)
                        
                        ## 5. Meta Description (max 155 karakter)
                        
                        ## 6. Anahtar Kelimeler (10 adet, virgülle ayrılmış)
                        
                        ## 7. Hashtag Önerileri (5 adet)
                        
                        Türkçe yaz.
                        """
                        
                        response = analyzer.model.generate_content(prompt)
                        
                        st.markdown("---")
                        st.markdown("### 📝 Üretilen İçerik")
                        st.markdown(response.text)
                        
                        st.download_button(
                            "📥 İçeriği İndir",
                            response.text,
                            file_name=f"urun_icerik_{datetime.now().strftime('%Y%m%d_%H%M')}.md",
                            mime="text/markdown"
                        )
                        
                    except Exception as e:
                        st.error(f"Hata: {str(e)}")
            else:
                st.warning("⚠️ Ürün adı girin.")
    
    with tab2:
        st.markdown("**Mevcut ürün açıklamasını iyileştirin:**")
        existing_content = st.text_area("📄 Mevcut Açıklama", height=150, placeholder="İyileştirmek istediğiniz metni yapıştırın...")
        
        improve_type = st.multiselect("🎯 İyileştirme Türü", 
                                       ["SEO Optimizasyonu", "Daha İkna Edici", "Daha Detaylı", "Daha Kısa", "Emoji Ekle"])
        
        if st.button("🔄 İyileştir", type="secondary"):
            if existing_content:
                with st.spinner("🤖 İyileştiriliyor..."):
                    try:
                        analyzer = GeminiAnalyzer()
                        prompt = f"""
                        Aşağıdaki ürün açıklamasını şu yönlerde iyileştir: {', '.join(improve_type)}
                        
                        Mevcut metin:
                        {existing_content}
                        
                        İyileştirilmiş versiyon:
                        """
                        response = analyzer.model.generate_content(prompt)
                        st.markdown("### ✨ İyileştirilmiş İçerik")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"Hata: {str(e)}")

# ============================================
# PAGE 6: AI ASSISTANT
# ============================================
elif page == "💬 AI Asistanı":
    st.subheader("💬 AI Pazar Asistanı")
    st.caption(f"📊 {selected_category} verileri hakkında sorular sorun.")

    if not st.session_state.get("chat_session"):
        try:
            analyzer = GeminiAnalyzer()
            st.session_state.chat_session = analyzer.create_chat_session(df)
        except Exception as e:
            st.error(f"Chat başlatılamadı: {e}")
            st.stop()
    
    # Quick Actions
    suggestions = [
        ("📊", "Pazar özeti"),
        ("💰", "En ucuz 5 ürün"),
        ("⭐", "En popüler ürünler"),
        ("🎯", "Fırsat analizi"),
        ("📝", "Strateji önerisi"),
        ("🔥", "Trend ürünler")
    ]
    
    cols = st.columns(6)
    prompt_selection = None
    
    for i, (emoji, text) in enumerate(suggestions):
        with cols[i]:
            if st.button(f"{emoji}", key=f"suggest_{i}", help=text):
                prompt_selection = text

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Chat container
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    prompt = st.chat_input("Soru sorun...")
    
    if prompt_selection:
        prompt = prompt_selection
    
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

            try:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    response = st.session_state.chat_session.send_message(prompt, stream=True)
                    
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Hata: {e}")

# ============================================
# PAGE 7: REPORT GENERATOR
# ============================================
elif page == "📄 Rapor Oluştur":
    st.subheader("📄 Profesyonel Rapor Oluşturucu")
    
    st.markdown("""
    > 📊 **Amaç:** Analizleri profesyonel bir rapor formatında dışa aktarın.
    """)
    
    report_type = st.selectbox("📋 Rapor Türü", [
        "📊 Tam Pazar Analizi",
        "💰 Fiyat Raporu",
        "📈 Rakip Analizi",
        "📝 Yönetici Özeti"
    ])
    
    include_options = st.multiselect("📎 Dahil Edilecek Bölümler", [
        "Pazar İstatistikleri",
        "Fiyat Analizi",
        "Segment Dağılımı",
        "Top Ürünler",
        "Marka Analizi",
        "SWOT Analizi",
        "Öneriler"
    ], default=["Pazar İstatistikleri", "Fiyat Analizi", "Top Ürünler", "Öneriler"])
    
    company_name = st.text_input("🏢 Şirket Adı", value="ESEY Kozmetik")
    
    if st.button("📄 Rapor Oluştur", type="primary"):
        with st.spinner("📝 Rapor hazırlanıyor..."):
            
            # Calculate stats
            avg_price = df["Fiyat_Clean"].mean()
            min_price = df["Fiyat_Clean"].min()
            max_price = df["Fiyat_Clean"].max()
            median_price = df["Fiyat_Clean"].median()
            total = len(df)
            
            report_content = f"""
# 📊 {selected_category} Pazar Analizi Raporu

**Hazırlayan:** {company_name}  
**Tarih:** {datetime.now().strftime('%d.%m.%Y')}  
**Veri Kaynağı:** Trendyol  
**Analiz Edilen Ürün:** {total} adet  

---

## 📈 Yönetici Özeti

Bu rapor, Trendyol platformundaki **{selected_category}** kategorisinin detaylı pazar analizini içermektedir. 
Toplam **{total}** ürün analiz edilmiş olup, fiyat aralığı **{min_price:.0f}₺ - {max_price:.0f}₺** arasında değişmektedir.

---

## 📊 Pazar İstatistikleri

| Metrik | Değer |
|--------|-------|
| Toplam Ürün | {total} |
| Ortalama Fiyat | {avg_price:.2f} ₺ |
| Medyan Fiyat | {median_price:.2f} ₺ |
| Minimum Fiyat | {min_price:.2f} ₺ |
| Maksimum Fiyat | {max_price:.2f} ₺ |
| Fiyat Aralığı | {max_price - min_price:.2f} ₺ |

---

## 💰 Fiyat Segmentasyonu

| Segment | Fiyat Aralığı | Ürün Sayısı |
|---------|---------------|-------------|
| 🟢 Ekonomik | 0 - {df["Fiyat_Clean"].quantile(0.25):.0f} ₺ | {len(df[df["Fiyat_Clean"] <= df["Fiyat_Clean"].quantile(0.25)])} |
| 🔵 Orta-Alt | {df["Fiyat_Clean"].quantile(0.25):.0f} - {median_price:.0f} ₺ | {len(df[(df["Fiyat_Clean"] > df["Fiyat_Clean"].quantile(0.25)) & (df["Fiyat_Clean"] <= median_price)])} |
| 🟡 Orta-Üst | {median_price:.0f} - {df["Fiyat_Clean"].quantile(0.75):.0f} ₺ | {len(df[(df["Fiyat_Clean"] > median_price) & (df["Fiyat_Clean"] <= df["Fiyat_Clean"].quantile(0.75))])} |
| 🔴 Premium | {df["Fiyat_Clean"].quantile(0.75):.0f} ₺ + | {len(df[df["Fiyat_Clean"] > df["Fiyat_Clean"].quantile(0.75)])} |

---

## 🏆 En Popüler Ürünler

"""
            # Add top products
            if "Yorum_Clean" in df.columns:
                top5 = df.nlargest(5, "Yorum_Clean")
                for i, row in top5.iterrows():
                    report_content += f"**{top5.index.get_loc(i)+1}.** {row['Ürün Adı']} - {row['Fiyat']} ₺ ({row['Yorum Sayısı']} yorum)\n\n"
            
            report_content += """
---

## 💡 Stratejik Öneriler

1. **Fiyat Optimizasyonu:** Ortalama fiyatın biraz altında konumlanarak rekabet avantajı sağlanabilir.

2. **Segment Odağı:** Orta segment en kalabalık olduğundan, farklılaşma için Ekonomik veya Premium segmentlere yönelmek değerlendirilebilir.

3. **İndirim Stratejisi:** Rakiplerin ortalama indirim oranları dikkate alınarak kampanya planlaması yapılmalıdır.

4. **İçerik Optimizasyonu:** SEO uyumlu ürün başlıkları ve açıklamaları ile organik görünürlük artırılabilir.

---

## 📝 Sonuç

{selected_category} pazarı yüksek rekabete sahip dinamik bir alan olup, veri odaklı karar alma ve sürekli optimizasyon gerektirmektedir. Bu rapordaki analizler ışığında stratejik adımlar atılması önerilmektedir.

---

*Bu rapor BTÜ-İMEP projesi kapsamında Yapay Zeka Destekli Trendyol Satış Optimizasyon Sistemi tarafından oluşturulmuştur.*

**Habib Salim | Bilgisayar Mühendisliği | 2025**
"""
            
            st.markdown("### 📄 Oluşturulan Rapor")
            st.markdown(report_content)
            
            # Download options
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    "📥 Markdown İndir",
                    report_content,
                    file_name=f"pazar_raporu_{selected_category}_{datetime.now().strftime('%Y%m%d')}.md",
                    mime="text/markdown"
                )
            
            with col2:
                # Simple HTML version
                html_content = f"""
                <html>
                <head>
                    <meta charset="utf-8">
                    <title>Pazar Raporu - {selected_category}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
                        h1 {{ color: #667eea; }}
                        table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                        th, td {{ border: 1px solid #ddd; padding: 10px; text-align: left; }}
                        th {{ background-color: #667eea; color: white; }}
                    </style>
                </head>
                <body>
                {report_content.replace('# ', '<h1>').replace('## ', '<h2>').replace('---', '<hr>').replace('|', '</td><td>')}
                </body>
                </html>
                """
                
                st.download_button(
                    "📥 HTML İndir",
                    html_content,
                    file_name=f"pazar_raporu_{selected_category}_{datetime.now().strftime('%Y%m%d')}.html",
                    mime="text/html"
                )

# Footer
st.sidebar.markdown("---")
st.sidebar.success("✅ Sistem Aktif")
st.sidebar.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M')}")
