
# app.py - Rename BP21 - Revisi ke-202507211940-1
import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
import zipfile

st.set_page_config(page_title="Rename Bukti Potong 21", layout="centered")

st.markdown("""
<style>
    .stApp {
        background-color: #0d1117;
        color: white;
    }
    h1, h2, h3, h4, h5, h6, p, label, .markdown-text-container, .stText, .stMarkdown {
        color: white !important;
    }
    .stButton>button, .stDownloadButton>button {
        background-color: #0070C0;
        color: white !important;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
</style>
""", unsafe_allow_html=True)

st.title("🧾 Rename Bukti Potong 21 (BP21)")
st.markdown("*By: Reza Fahlevi Lubis BKP @zavibis*")

st.markdown("""
### 📌 Petunjuk Penggunaan
1. Upload satu atau beberapa file PDF Bukti Potong 21.
2. Aplikasi akan membaca informasi dari PDF.
3. Pilih kolom untuk dijadikan format nama file.
4. Klik **Rename PDF & Download** untuk mengunduh hasil.
""")

def extract_regex(text, label, after_label=True, default=""):
    pattern = rf"{re.escape(label)}\s*:?\s*(.+)" if after_label else rf"{re.escape(label)}"
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else default

def extract_data_bp21(file_like):
    with pdfplumber.open(file_like) as pdf:
        full_text = "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

    data = {}
    data["SIFAT PEMOTONGAN"] = extract_regex(full_text, "SIFAT PEMOTONGAN")
    data["STATUS BUKTI PEMOTONGAN"] = extract_regex(full_text, "STATUS BUKTI PEMOTONGAN")
    data["NIK/NPWP PENERIMA PENGHASILAN"] = extract_regex(full_text, "NIK / NPWP")
    data["Nama PENERIMA PENGHASILAN"] = extract_regex(full_text, "NAMA", default="TIDAK_DIKETAHUI")
    data["NITKU PENERIMA PENGHASILAN"] = extract_regex(full_text, "NOMOR IDENTITAS")

    data["Jenis fasilitas"] = extract_regex(full_text, "Jenis Fasilitas")
    data["KODE OBJEK PAJAk"] = extract_regex(full_text, "Kode Objek Pajak")
    data["OBJEK PAJAK"] = extract_regex(full_text, "Nama Objek Pajak")
    data["PENGHASILAN BRUTO"] = extract_regex(full_text, "Penghasilan Bruto")
    data["DPP (%)"] = extract_regex(full_text, "DPP (%)")
    data["TARIF (%)"] = extract_regex(full_text, "Tarif (%)")
    data["Pph Dipotong (Rp)"] = extract_regex(full_text, "PPh Dipotong")
    data["Dokumen Referensi"] = extract_regex(full_text, "Dokumen Referensi")
    data["jenis dokumen"] = extract_regex(full_text, "Jenis Dokumen")
    data["Tanggal Dokumen"] = extract_regex(full_text, "Tanggal")
    data["Nomor Dokumen"] = extract_regex(full_text, "Nomor Dokumen")

    data["NPWP/NIK Pemotong"] = extract_regex(full_text, "C.1 NPWP / NIK")
    data["NITKU Pemotong"] = extract_regex(full_text, "C.2 NOMOR IDENTITAS")
    data["NAMA PEMOTONG Pemotong"] = extract_regex(full_text, "C.3 NAMA PEMOTONG", default="TANPA_NAMA")
    data["TANGGAL Pemotong"] = extract_regex(full_text, "C.4 TANGGAL")
    data["NAMA PENANDATANGAN"] = extract_regex(full_text, "C.5 NAMA PENANDATANGAN")
    return data

def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", str(text))

def generate_filename(row, selected_cols):
    parts = [sanitize_filename(str(row.get(col, ''))) for col in selected_cols]
    parts = [p if p else "NA" for p in parts]
    return "BP21_" + "_".join(parts) + ".pdf"

uploaded_files = st.file_uploader("📎 Upload PDF Bukti Potong 21", type=["pdf"], accept_multiple_files=True)

if uploaded_files:
    data_rows = []
    for file in uploaded_files:
        pdf_bytes = file.read()
        data = extract_data_bp21(BytesIO(pdf_bytes))
        data["OriginalName"] = file.name
        data["FileBytes"] = pdf_bytes
        data_rows.append(data)

    df = pd.DataFrame(data_rows).drop(columns=["FileBytes", "OriginalName"])
    st.dataframe(df)  # preview

    selected_cols = st.multiselect("### ✏️ Pilih Kolom untuk Rename", df.columns.tolist())

    if st.button("🔁 Rename PDF & Download"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for i, row in df.iterrows():
                filename = generate_filename(row, selected_cols)
                zipf.writestr(filename, data_rows[i]["FileBytes"])
        zip_buffer.seek(0)
        st.success("✅ Siap diunduh!")
        st.download_button("📦 Download ZIP", zip_buffer, file_name="bp21_renamed.zip", mime="application/zip")
