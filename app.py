import streamlit as st
import pdfplumber
from deep_translator import GoogleTranslator
from fpdf import FPDF
import time

# --- 1. CONFIGURATIE ---
st.set_page_config(page_title="Gratis PDF Vertaler", layout="centered")

# --- 2. FUNCTIES ---

def create_pdf(text):
    """Probeert een PDF te maken. Geeft None terug als het mislukt."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=10)
        
        # Encoding fix voor speciale tekens
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        for line in safe_text.split('\n'):
            if line.strip() == "":
                pdf.ln(5)
            else:
                pdf.multi_cell(0, 8, txt=line)
        
        return pdf.output()
    except Exception as e:
        st.error(f"Fout tijdens maken van PDF: {e}")
        return None

# --- 3. GEHEUGEN INSTELLEN ---
# Dit zorgt ervoor dat de vertaling niet verdwijnt als je ergens op klikt
if 'vertaalde_tekst' not in st.session_state:
    st.session_state['vertaalde_tekst'] = ""

# --- 4. DE APP ---
st.title("🌍 PDF Vertaler (Failsafe Versie)")

uploaded_file = st.file_uploader("Stap 1: Upload je PDF", type="pdf")
target_lang = st.selectbox("Stap 2: Kies taal", ["nl", "en", "de", "fr", "es", "it"])

# Knop om te starten
if uploaded_file is not None:
    if st.button("🚀 Start Vertaling"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        temp_text = ""
        
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                total_pages = len(pdf.pages)
                
                for i, page in enumerate(pdf.pages):
                    raw_text = page.extract_text()
                    if raw_text:
                        # Vertaal stukje
                        translated = GoogleTranslator(source='auto', target=target_lang).translate(raw_text)
                        temp_text += f"--- Pagina {i+1} ---\n{translated}\n\n"
                    
                    # Update voortgang
                    progress_bar.progress((i + 1) / total_pages)
                    status_text.text(f"Bezig met pagina {i+1} van {total_pages}...")
                    
                    # Pauze tegen blokkades
                    time.sleep(1.0)
            
            # Sla het resultaat op in het geheugen!
            st.session_state['vertaalde_tekst'] = temp_text
            st.success("Klaar! Scroll naar beneden voor de knoppen.")
            
        except Exception as e:
            st.error(f"Er ging iets mis tijdens het vertalen: {e}")

# --- 5. DOWNLOAD KNOPPEN (Staan hier los, zodat ze altijd zichtbaar zijn) ---

st.divider() # Een lijntje voor de duidelijkheid

if st.session_state['vertaalde_tekst'] != "":
    st.subheader("📥 Je downloads staan klaar")
    
    # KNOP 1: TEKST (Werkt altijd)
    st.download_button(
        label="📄 Download als Tekstbestand (.txt)",
        data=st.session_state['vertaalde_tekst'],
        file_name="vertaling.txt",
        mime="text/plain",
        key="btn_txt"
    )
    
    # KNOP 2: PDF (Proberen we te maken)
    pdf_data = create_pdf(st.session_state['vertaalde_tekst'])
    
    if pdf_data:
        st.download_button(
            label="📕 Download als PDF bestand",
            data=bytes(pdf_data),
            file_name="vertaling.pdf",
            mime="application/pdf",
            key="btn_pdf"
        )
    else:
        st.warning("De PDF kon niet gemaakt worden (waarschijnlijk vreemde tekens), maar je kunt wel het tekstbestand hierboven downloaden!")

else:
    # Als er nog niks vertaald is, laten we dit zien:
    st.info("Nog geen vertaling beschikbaar. Upload een bestand en klik op Start.")
