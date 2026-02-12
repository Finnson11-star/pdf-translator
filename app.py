import streamlit as st
import pdfplumber
from deep_translator import GoogleTranslator
from fpdf import FPDF
import time

# Functie om de vertaalde tekst om te zetten naar een PDF-bestand
def create_pdf(text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("helvetica", size=10)
    
    for line in text.split('\n'):
        # Filter vreemde tekens die FPDF niet begrijpt
        clean_line = line.encode('latin-1', 'ignore').decode('latin-1')
        pdf.multi_cell(0, 8, txt=clean_line)
    return pdf.output()

# --- Streamlit Interface ---
st.set_page_config(page_title="Gratis PDF Vertaler", layout="wide")
st.title("🌍 PDF Vertaler (Onbeperkt aantal pagina's)")
st.info("Deze app vertaalt pagina voor pagina om blokkades te voorkomen. Even geduld bij grote bestanden!")

uploaded_file = st.file_uploader("Upload je PDF bestand", type="pdf")
target_lang = st.sidebar.selectbox("Vertaal naar taal:", ["nl", "en", "de", "fr", "es", "it"])

if uploaded_file is not None:
    if st.button("Start de Vertaling"):
        vertaalde_tekst = ""
        
        with pdfplumber.open(uploaded_file) as pdf:
            totaal_paginas = len(pdf.pages)
            progress_bar = st.progress(0)
            status_tekst = st.empty()
            preview_tekst = st.empty() # Plek voor de live preview

            for i, pagina in enumerate(pdf.pages):
                tekst = pagina.extract_text()
                
                if tekst:
                    try:
                        # Vertaling uitvoeren per pagina
                        vertaling = GoogleTranslator(source='auto', target=target_lang).translate(tekst)
                        vertaalde_tekst += f"--- Pagina {i+1} ---\n{vertaling}\n\n"
                        
                        # Laat de gebruiker zien wat er gebeurt
                        with preview_tekst.container():
                            st.write(f"**Laatst vertaalde pagina ({i+1}):**")
                            st.text(vertaling[:500] + "...") # Toon eerste 500 tekens
                            
                    except Exception as e:
                        st.error(f"Google pauzeert de verbinding op pagina {i+1}. Download wat tot nu toe klaar is.")
                        break
                
                # Update voortgangsbalk
                voortgang = (i + 1) / totaal_paginas
                progress_bar.progress(voortgang)
                status_tekst.text(f"Bezig met pagina {i+1} van {totaal_paginas}...")
                
                # Pauze van 1.5 seconde om 'bot-detectie' te omzeilen
                time.sleep(1.5)

        st.success("Vertaling is voltooid!")

        # Download sectie
        pdf_output = create_pdf(vertaalde_tekst)
        st.download_button(
            label="📥 Download Vertaalde PDF",
            data=bytes(pdf_output),
            file_name="vertaald_document.pdf",
            mime="application/pdf"
        )
