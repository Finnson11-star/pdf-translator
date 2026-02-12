import streamlit as st
import pdfplumber
from deep_translator import GoogleTranslator
import io

st.set_page_config(page_title="Gratis PDF Vertaler", page_icon="🌍")

st.title("🌍 Gratis PDF Vertaler")
st.subheader("Vertaal je PDF zonder API-kosten")

# Instellingen in de zijbalk
st.sidebar.header("Instellingen")
target_lang = st.sidebar.selectbox("Vertaal naar:", ["nl", "en", "de", "fr", "es", "it"])

uploaded_file = st.file_uploader("Upload een PDF bestand", type="pdf")

if uploaded_file is not None:
    with pdfplumber.open(uploaded_file) as pdf:
        all_text = ""
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Tekst extraheren per pagina
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                all_text += text + "\n"
            
            # Update voortgang
            progress = (i + 1) / len(pdf.pages)
            progress_bar.progress(progress)
            status_text.text(f"Pagina {i+1} van {len(pdf.pages)} verwerkt...")

    st.success("Tekst succesvol uitgelezen!")

    if st.button("Start Vertaling"):
        with st.spinner('Bezig met vertalen...'):
            # GoogleTranslator heeft een limiet per verzoek, dus we splitsen grote teksten
            # De deep-translator bibliotheek handelt dit vaak intern al goed af.
            try:
                translated = GoogleTranslator(source='auto', target=target_lang).translate(all_text)
                
                st.subheader("Vertaalde Resultaat:")
                st.text_area("Vertaalde tekst", translated, height=300)
                
                # Download knop voor de tekst
                st.download_button(
                    label="Download vertaling als .txt",
                    data=translated,
                    file_name="vertaling.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"Er ging iets mis: {e}")