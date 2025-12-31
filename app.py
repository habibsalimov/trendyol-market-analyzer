import streamlit as st
import pandas as pd
import os
import glob
from src.analysis.gemini_analyzer import GeminiAnalyzer
from dotenv import load_dotenv

# Load environment variables for API key
load_dotenv()

st.set_page_config(page_title="Trendyol Market Analyzer", page_icon="📊", layout="wide")

st.title("📊 Trendyol Kozmetik Pazar Analizi")
st.markdown("Bu araç, Trendyol'dan çekilen verileri analiz eder ve AI destekli içgörüler sunar.")

# Sidebar - Navigation
page = st.sidebar.radio("Mod Seçimi", ["📋 Analiz Raporu", "💬 AI Asistanı"])

# Sidebar - Category Selection
st.sidebar.markdown("---")
st.sidebar.header("Kategori Seçimi")
output_files = glob.glob("outputs/output_*.xlsx")
# ... existing category selection logic ...
categories = [f.split("output_")[-1].replace(".xlsx", "") for f in output_files]

if not categories:
    st.sidebar.warning("Henüz veri bulunamadı. Lütfen önce veri çekme işlemini başlatın.")
    st.stop()

selected_category = st.sidebar.selectbox("Analiz Edilecek Kategori", categories)
file_path = f"outputs/output_{selected_category}.xlsx"

# ... Session state reset logic ...
if "current_category" not in st.session_state:
    st.session_state.current_category = None

if st.session_state.current_category != selected_category:
    st.session_state.chat_session = None
    st.session_state.chat_history = []
    st.session_state.analysis_report = None
    st.session_state.current_category = selected_category
    st.session_state.messages = [] # Clear messages on category change

# PAGE 1: ANALYSIS REPORT
if page == "📋 Analiz Raporu":
    st.subheader(f"📊 {selected_category} - Pazar Analizi")
    
    # Persistence Path
    report_cache_path = f"outputs/analysis_{selected_category}_report.md"
    
    # Auto-load logic
    if st.session_state.analysis_report is None and os.path.exists(report_cache_path):
        with open(report_cache_path, "r", encoding="utf-8") as f:
            st.session_state.analysis_report = f.read()
            # Also need to wake up chat session
            analyzer = GeminiAnalyzer()
            df = pd.read_excel(file_path)
            st.session_state.chat_session = analyzer.create_chat_session(df)
            st.info("💾 Önceki analiz başarıyla yüklendi.")

    # Button Logic
    button_label = "🚀 Analizi Başlat"
    if st.session_state.analysis_report:
        button_label = "🔄 Analizi Yenile"
        
    if st.button(button_label, type="primary"):
        with st.spinner(f"{selected_category} kategorisi analiz ediliyor..."):
            try:
                analyzer = GeminiAnalyzer()
                # Generate Report
                report = analyzer.analyze_category(file_path)
                st.session_state.analysis_report = report
                
                # Save to Cache
                with open(report_cache_path, "w", encoding="utf-8") as f:
                    f.write(report)
                
                # Create Chat Session
                df = pd.read_excel(file_path)
                st.session_state.chat_session = analyzer.create_chat_session(df)
                
                st.success("Analiz Tamamlandı ve Kaydedildi!")
            except Exception as e:
                st.error(f"Bir hata oluştu: {str(e)}")

    # Display Report if available
    if st.session_state.get("analysis_report"):
        st.markdown("---")
        
        import re
        
        # Custom CSS for smaller text in expanders
        st.markdown("""
            <style>
            .streamlit-expanderContent p, .streamlit-expanderContent li, .streamlit-expanderContent div {
                font-size: 14px !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        report_text = st.session_state.analysis_report
        sections = report_text.split("---")
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            lines = section.split('\n')
            title = "Ürün Detayı"
            content = section
            
            # Helper to extract link from title
            url_match = None
            if lines and (lines[0].startswith("###") or lines[0].startswith("**")):
                raw_title = lines[0].replace("#", "").strip()
                # Check for Markdown link: [Title](URL)
                match = re.search(r'\[(.*?)\]\((.*?)\)', raw_title)
                if match:
                    title = match.group(1) # Detailed Name
                    url = match.group(2)   # The URL
                    # Prepend link to content
                    content = f"**🔗 [Ürüne Git ve İncele]({url})**\n\n" + "\n".join(lines[1:])
                else:
                    title = raw_title
                    content = "\n".join(lines[1:])
                
            with st.expander(title):
                st.markdown(content)

# PAGE 2: AI ASSISTANT
elif page == "💬 AI Asistanı":
    st.subheader("💬 AI Asistanı ile Sohbet")
    st.caption(f"{selected_category} verileri hakkında sorular sorun.")

    if not st.session_state.get("chat_session"):
        st.info("⚠️ Lütfen önce 'Analiz Raporu' sekmesinden analizi başlatın.")
    else:
        # Suggested Prompts
        suggestions = [
            "En uygun fiyatlı ürün hangisi?",
            "En yüksek puanlı/yorumlu ürün hangisi?",
            "Bu pazarda nasıl bir fırsat var?",
            "İsimlendirme için 3 yaratıcı öneri ver."
        ]
        
        cols = st.columns(4)
        prompt_selection = None
        
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(suggestion, key=f"suggest_{i}"):
                    prompt_selection = suggestion

        # Initialize chat history for display if needed
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Chat Input
        prompt = st.chat_input("Bu ürünlerle ilgili ne merak ediyorsunuz?")
        
        # Handle suggested prompt selection
        if prompt_selection:
            prompt = prompt_selection
        
        if prompt:
            # Add user message to UI
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Get response from Gemini
            try:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    with st.spinner('Yapay Zeka düşünüyor...'):
                        # Send message with stream=True
                        response = st.session_state.chat_session.send_message(prompt, stream=True)
                    
                    # Accumulate and display
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            # Add a blinking cursor effect
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Final update without cursor
                    message_placeholder.markdown(full_response)
                
                # Add assistant message to UI history
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                st.error(f"Mesaj gönderilemedi: {e}")
            
            # Rerun to update the chat history visually immediately
            # st.rerun() # Removed rerun as it causes re-execution. Streamlit handles chat history append locally fine. only needed if state desyncs.
            # Actually, without rerun, the history list doesn't get updated in the loop above on next run start? 
            # Streamlit's chat_message + session_state append pattern usually works without rerun for the current interaction, 
            # but rerunning ensures consistent state. Let's keep it but careful about loop.
            # With streaming, we rendered it manually. The history append is for the NEXT reload. 
            pass
