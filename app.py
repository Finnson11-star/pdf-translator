import streamlit as st
import pdfplumber
from deep_translator import GoogleTranslator
from fpdf import FPDF
import time
import io

# --- STAP 1: CONFIGURATIE ---
st.set_page_config(page_title="Ultimate PDF Translator", layout="wide")

# --- STAP 2: HELPER FUNCTIES ---

def text_to_pdf(text_content):
    """Maakt een PDF van tekst en geeft de ruwe bytes terug."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=11)
        
        # Filter tekens die PDF niet aankan (latin-1 encoding)
        clean_text = text_content.encode('latin-1', 'replace').decode('latin-1')
        
        for line in clean_text.split('\n'):
            pdf.multi_cell(0, 7, txt=line)
        
        return pdf.output()
    except Exception as e:
        return None

# --- STAP 3: GEHEUGEN (Session State) ---
# We initialiseren hier de variabelen die de app moet onthouden
if 'final_translation' not in st.session_state:
    st.session_state.final_translation = None
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

# --- STAP 4: DE INTERFACE ---
st.title("🌍 De Ultieme PDF Vertaler")
st.write("Vertaal documenten pagina voor pagina zonder kosten.")

# Sidebar voor instellingen
with st.sidebar:
    st.header("Instellingen")
    target_lang = st.selectbox("Naar welke taal?", ["nl", "en", "de", "fr", "es", "it"])
    st.write("---")
    if st.button("Reset App"):
        st.session_state.final_translation = None
        st.rerun()

# Bestand uploaden
uploaded_file = st.file_uploader("Upload hier je PDF bestand", type=["pdf"])

if uploaded_file and st.session_state.final_translation is None:
    if st.button("🚀 Start Vertaling", use_container_width=True):
        st.session_state.is_processing = True
        full_output = ""
        
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                num_pages = len(pdf.pages)
                bar = st.progress(0)
                status = st.empty()
                
                for i in range(num_pages):
                    status.info(f"Bezig met pagina {i+1} van {num_pages}...")
                    page_text = pdf.pages[i].extract_text()
                    
                    if page_text:
                        # Vertaal de tekst van deze pagina
                        translation = GoogleTranslator(source='auto', target=target_lang).translate(page_text)
                        full_output += f"--- PAGINA {i+1} ---\n{translation}\n\n"
                    
                    # Voortgang bijwerken
                    bar.progress((i + 1) / num_pages)
                    # Kleine pauze om Google te vriend te houden
                    time.sleep(1.2)
                
                st.session_state.final_translation = full_output
                st.session_state.is_processing = False
                st.rerun() # Forceer herladen om de knoppen te tonen
        except Exception as e:
            st.error(f"Er is een fout opgetreden: {e}")
            st.session_state.is_processing = False

# --- STAP 5: HET DOWNLOAD GEDEELTE ---
# Dit gedeelte wordt pas getoond als de vertaling klaar is
if st.session_state.final_translation:
    st.success("✅ Vertaling voltooid!")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Optie 1: PDF Document")
        pdf_data = text_to_pdf(st.session_state.final_translation)
        if pdf_data:
            st.download_button(
                label="📥 Download als PDF",
                data=bytes(pdf_data),
                file_name="vertaald_document.pdf",
                mime="application/pdf"
            )
        else:
            st.error("PDF maken mislukt. Gebruik de tekstoptie.")

    with col2:
        st.subheader("Optie 2: Tekstbestand")
        st.download_button(
            label="📄 Download als .txt",
            data=st.session_state.final_translation,
            file_name="vertaald_document.txt",
            mime="text/plain"
        )
    
    st.write("---")
    st.write("**Voorbeeld van de vertaalde tekst:**")
    st.text_area("", st.session_state.final_translation, height=300)
