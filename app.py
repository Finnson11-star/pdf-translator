import streamlit as st
import pdfplumber
from deep_translator import GoogleTranslator
from fpdf import FPDF
import time

# --- 1. Functie voor PDF generatie ---
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # We gebruiken Helvetica, een standaard font dat bijna altijd werkt
    pdf.set_font("helvetica", size=10)
    
    # Belangrijk: we filteren de tekst zodat FPDF niet vastloopt op vreemde tekens
    # 'latin-1' is de standaard voor FPDF; 'replace' vervangt onbekende tekens door ?
    safe_text = text.encode('latin-1', 'replace').decode('latin-1')
    
    for line in safe_text.split('\n'):
        if line.strip() == "":
            pdf.ln(5) # Voeg een witregel toe
        else:
            # multi_cell zorgt voor tekstomloop binnen de marges
            pdf.multi_cell(0, 8, txt=line)
    
    return pdf.output()

# --- 2. Streamlit Interface ---
st.set_page_config(page_title="Gratis PDF Vertaler", layout="centered")
st.title("🌍 PDF Vertaler (Grote Bestanden)")
st.markdown("Vertaalt je PDF pagina voor pagina om blokkades te voorkomen.")

uploaded_file = st.file_uploader("Upload je PDF", type="pdf")
target_lang = st.sidebar.selectbox("Vertaal naar:", ["nl", "en", "de", "fr", "es", "it"])

if uploaded_file is not None:
    if st.button("Start Vertaling"):
        vertaalde_tekst = ""
        
        with pdfplumber.open(uploaded_file) as pdf:
            totaal_paginas = len(pdf.pages)
            progress_bar = st.progress(0)
            status_tekst = st.empty()
            preview_box = st.empty()

            for i, pagina in enumerate(pdf.pages):
                tekst_origineel = pagina.extract_text()
                
                if tekst_origineel:
                    try:
                        # Vertalen
                        vertaling = GoogleTranslator(source='auto', target=target_lang).translate(tekst_origineel)
                        vertaalde_tekst += f"--- Pagina {i+1} ---\n{vertaling}\n\n"
                        
                        # Live preview tonen
                        with preview_box.container():
                            st.write(f"✅ Pagina {i+1} vertaald...")
                            
                    except Exception as e:
                        st.error(f"Google heeft de verbinding gepauzeerd op pagina {i+1}. Je kunt downloaden wat er tot nu toe is.")
                        break
                
                # Voortgangsbalk updaten
                voortgang = (i + 1) / totaal_paginas
                progress_bar.progress(voortgang)
                status_tekst.text(f"Bezig met pagina {i+1} van {totaal_paginas}")
                
                # Korte pauze tegen bot-detectie
                time.sleep(1.5)

        st.success("Klaar!")

        # --- 3. Download Sectie ---
        if vertaalde_tekst:
            try:
                # Genereer PDF bytes
                pdf_bytes = create_pdf(vertaalde_tekst)
                
                st.download_button(
                    label="📥 Download Vertaalde PDF",
                    data=pdf_bytes,
                    file_name="vertaald_document.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.warning("De PDF kon niet worden gegenereerd door speciale tekens. Gebruik de tekst-optie hieronder.")
                st.error(f"Details: {e}")

            # Altijd een tekst-reserve optie bieden
            st.download_button(
                label="📄 Download als Tekstbestand (.txt)",
                data=vertaalde_tekst,
                file_name="vertaling.txt",
                mime="text/plain"
            )
