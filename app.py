import streamlit as st
import pdfplumber
from deep_translator import GoogleTranslator
from fpdf import FPDF
import time

# --- CONFIGURATIE ---
st.set_page_config(page_title="Gratis PDF Vertaler", layout="centered", page_icon="🌍")

# --- FUNCTIES ---

def create_pdf(text):
    """Genereert een PDF bestand van een string."""
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("helvetica", size=10)
        
        # Encoding fix: vervang onbekende tekens door ? om crashes/lege pagina's te voorkomen
        safe_text = text.encode('latin-1', 'replace').decode('latin-1')
        
        for line in safe_text.split('\n'):
            if line.strip() == "":
                pdf.ln(5) # Witregel
            else:
                # multi_cell zorgt voor automatische terugloop van tekst
                pdf.multi_cell(0, 8, txt=line)
        
        # output() geeft de bytes terug die nodig zijn voor de downloadknop
        return pdf.output()
    except Exception as e:
        st.error(f"Fout in PDF generator: {e}")
        return None

def vertaal_document(uploaded_file, target_lang):
    """Leest PDF, vertaalt pagina voor pagina en update de voortgang."""
    vertaalde_tekst_totaal = ""
    
    with pdfplumber.open(uploaded_file) as pdf:
        totaal_paginas = len(pdf.pages)
        
        # UI elementen voor voortgang
        progress_bar = st.progress(0)
        status_text = st.empty()
        preview_box = st.expander("Live voorbeeld van vertaling", expanded=True)
        
        for i, pagina in enumerate(pdf.pages):
            tekst = pagina.extract_text()
            
            if tekst:
                try:
                    # De vertaling aanroepen
                    vertaler = GoogleTranslator(source='auto', target=target_lang)
                    vertaling = vertaler.translate(tekst)
                    
                    # Toevoegen aan het totaal
                    vertaalde_tekst_totaal += f"--- Pagina {i+1} ---\n\n{vertaling}\n\n"
                    
                    # Update het voorbeeld venster
                    preview_box.write(f"✅ Pagina {i+1} vertaald...")
                    
                except Exception as e:
                    st.warning(f"Pagina {i+1} overgeslagen of pauze nodig: {e}")
                    time.sleep(2) # Extra pauze bij fout
            
            # Voortgang bijwerken
            progress_bar.progress((i + 1) / totaal_paginas)
            status_text.text(f"Bezig met verwerken: Pagina {i+1} van {totaal_paginas}")
            
            # Pauze om IP-blokkade te voorkomen
            time.sleep(1.5)
            
        progress_bar.empty()
        status_text.empty()
        
    return vertaalde_tekst_totaal

# --- HOOFD PROGRAMMA ---

st.title("🌍 PDF Vertaler Pro")
st.markdown("Upload een PDF, kies een taal en download het resultaat.")

# Sessie status initialiseren (Dit zorgt dat de download knop blijft staan!)
if 'vertaalde_tekst' not in st.session_state:
    st.session_state['vertaalde_tekst'] = ""

# 1. Upload Sectie
uploaded_file = st.file_uploader("Kies je bestand", type="pdf")
target_lang = st.selectbox("Vertaal naar:", 
                           options=["nl", "en", "de", "fr", "es", "it"],
                           format_func=lambda x: x.upper())

# 2. Vertaal Knop
if uploaded_file is not None:
    if st.button("🚀 Start Vertaling", type="primary"):
        with st.spinner("Bezig met vertalen... Dit kan even duren."):
            # Voer de vertaling uit en sla op in session_state
            resultaat = vertaal_document(uploaded_file, target_lang)
            st.session_state['vertaalde_tekst'] = resultaat
            st.success("Vertaling voltooid! Zie de knoppen hieronder.")

# 3. Download Sectie (Alleen tonen als er tekst in het geheugen zit)
if st.session_state['vertaalde_tekst']:
    st.divider()
    st.subheader("📥 Je bestanden staan klaar")
    
    col1, col2 = st.columns(2)
    
    # PDF Generatie en Knop
    pdf_bytes = create_pdf(st.session_state['vertaalde_tekst'])
    if pdf_bytes:
        col1.download_button(
            label="Download als PDF",
            data=bytes(pdf_bytes),
            file_name="vertaald_document.pdf",
            mime="application/pdf",
            key="pdf-btn"
        )
    
    # Tekst Knop (Backup)
    col2.download_button(
        label="Download als Tekst (.txt)",
        data=st.session_state['vertaalde_tekst'],
        file_name="vertaald_document.txt",
        mime="text/plain",
        key="txt-btn"
    )

    # Optie om opnieuw te beginnen
    if st.button("Nieuw bestand vertalen"):
        st.session_state['vertaalde_tekst'] = ""
        st.rerun()
