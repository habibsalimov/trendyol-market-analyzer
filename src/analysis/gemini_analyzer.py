
import os
import pandas as pd
import google.generativeai as genai
from decouple import config

class GeminiAnalyzer:
    def __init__(self):
        deployment_mode = config("DEPLOYMENT_MODE", default="LOCAL")
        if deployment_mode == "LOCAL":
             api_key = config("GEMINI_API_KEY", default=None)
        else:
             # In production/cloud, might use different auth
             api_key = os.getenv("GEMINI_API_KEY")
             
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env or environment variables.")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3-flash-preview')

    def analyze_category(self, file_path):
        """
        Reads an Excel file, summarizes it, and sends it to Gemini for analysis.
        """
        try:
            df = pd.read_excel(file_path)
            if df.empty:
                return "No data found in file."

            # Prepare data summary to avoid sending too many tokens if list is huge
            # We'll send the first 20 rows for detailed product-by-product analysis
            
            summary_stats = df.describe().to_string()
            
            # Calculate average price for context
            try:
                avg_price = df["Fiyat"].mean()
            except:
                avg_price = "Bilinmiyor"

            # Convert first 20 rows to JSON format to ensure full URLs are preserved
            sample_data = df.head(20).to_json(orient='records', force_ascii=False)
            
            category_name = file_path.split("_")[-1].replace(".xlsx", "")

            prompt = f"""
            Bir Kozmetik Şirketi için Ürün Geliştirme ve Pazarlama Stratejisti olarak hareket et.
            
            Büyük bir e-ticaret sitesinden (Trendyol) şu kategori için ürün verilerini topladım: {category_name}.
            Pazarın Ortalama Fiyatı: {avg_price}
            
            Aşağıdaki JSON verisinde yer alan **HER BİR ÜRÜN İÇİN** (Toplam 20 adet) sırasıyla mikro analiz yapmanı istiyorum.
            
            Ürün Verisi (JSON):
            {sample_data}
            
            **İstenen Çıktı Formatı (Her ürün için tekrarlanmalı):**
            
            ---
            ### [Sıra No]. [[Ürün Adı]](Ürün Linki)
            **ÖNEMLİ:** Ürün başlığını mutlaka verideki 'Ürün Linki' değerini kullanarak TIKLANABİLİR LİNK formatında yaz.
            
            *   **Fiyat Analizi:** Ürün fiyatı ({avg_price:.2f} ortalamasına göre) rekabetçi mi? Pahalı mı ucuz mu kalıyor?
            *   **İsimlendirme Puanı (1-10):** Ürün ismi yeterince açıklayıcı ve "clickbait" mi?
            *   **Eksik/Hata:** İlanda gördüğün bariz bir eksiklik var mı? (Örn: Gramaj yazmıyor, faydası belirsiz)
            *   **Biz Olsak Nasıl Satardık?:** Bu ürünü daha çok satmak için tek bir "Vurucu Cümle" veya strateji öner.
            ---
            
            Lütfen analizi tamamen TÜRKÇE yap ve her ürün için ayrı ayrı başlık aç. Genel özet istemiyorum, ürün bazlı detay istiyorum.
            """
            
            response = self.model.generate_content(prompt)
            return response.text

        except Exception as e:
            return f"Error analyzing {file_path}: {str(e)}"
    def create_chat_session(self, df):
        """
        Creates a chat session initialized with the provided dataframe context.
        """
        try:
            # Prepare data context - Use JSON to preserve full URLs
            sample_data = df.to_json(orient='records', force_ascii=False)
            
            # Initial system message / context setting
            history = [
                {
                    "role": "user",
                    "parts": [
                        f"""Sen bir Kozmetik Ürün ve Pazar Analisti'sin. Aşağıdaki veri setindeki ürünler hakkında soruları cevaplayacaksın.
                        
                        **ÖNEMLİ KURAL:** Cevabında listedeki herhangi bir üründen bahsettiğinde, KESİNLİKLE 'Ürün Linki' alanını kullanarak o ürüne tıklanabilir link vermelisin.
                        Format şu olmalı: `[Ürün Adı](Ürün Linki)`
                        
                        Veri Seti (JSON):
                        {sample_data}
                        
                        Lütfen Türkçe cevap ver."""
                    ]
                },
                {
                    "role": "model",
                    "parts": [
                        "Anlaşıldı. Veri setini inceledim ve Kozmetik Pazar Analisti olarak sorularınızı cevaplamaya hazırım."
                    ]
                }
            ]
            
            chat_session = self.model.start_chat(history=history)
            return chat_session
        except Exception as e:
            print(f"Error creating chat session: {e}")
            return None
