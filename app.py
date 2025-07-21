
# app.py - Rename BP21 - Revisi ke-202507212020-1
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
st.markdown("Aplikasi ini digunakan untuk mengganti nama file PDF Bukti Potong 21 secara otomatis berdasarkan data yang diekstrak dari file.")
st.markdown("*By: Reza Fahlevi Lubis BKP @zavibis*")

def regex(text, pattern, group=1, default=""):
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(group).strip() if match else default

def extract_objek_pajak_info(text):
    match = re.search(r"(Imbalan[^\n]*?)\s+(\d[\d\.]+)\s+(\d+)\s+(\d+)\s+(\d[\d\.]+)", text)
    if match:
        return {
            "OBJEK PAJAK": match.group(1).strip(),
            "PENGHASILAN BRUTO": match.group(2).replace(".", ""),
            "DPP (%)": match.group(3),
            "TARIF (%)": match.group(4),
            "Pph Dipotong (Rp)": match.group(5).replace(".", "")
        }
    return {
        "OBJEK PAJAK": "", "PENGHASILAN BRUTO": "", "DPP (%)": "", "TARIF (%)": "", "Pph Dipotong (Rp)": ""
    }

def extract_data_bp21(file_like):
    with pdfplumber.open(file_like) as pdf:
        text = "\n".join(p.extract_text() for p in pdf.pages if p.extract_text())

    data = {}
    match = re.search(r"(\S+)\s+(\d{2}-\d{4})\s+(FINAL|TIDAK FINAL)\s+(NORMAL|PEMBETULAN)", text)
    if match:
        data["NOMOR BUKTI PEMOTONGAN"] = match.group(1)
        data["MASA PAJAK"] = match.group(2)
        data["SIFAT PEMOTONGAN"] = match.group(3)
        data["STATUS BUKTI PEMOTONGAN"] = match.group(4)
    else:
        data["NOMOR BUKTI PEMOTONGAN"] = ""
        data["MASA PAJAK"] = ""
        data["SIFAT PEMOTONGAN"] = ""
        data["STATUS BUKTI PEMOTONGAN"] = ""

    data["NIK/NPWP PENERIMA PENGHASILAN"] = regex(text, r"A\.1 NIK/NPWP\s*:\s*(\d+)")
    data["Nama PENERIMA PENGHASILAN"] = regex(text, r"A\.2 Nama\s*:\s*(.+)")
    data["NITKU PENERIMA PENGHASILAN"] = regex(text, r"A\.3 NITKU\s*:\s*(\d+)")

    data["Jenis fasilitas"] = regex(text, r"B\.1 Jenis Fasilitas\s*:\s*(.+)")
    data["KODE OBJEK PAJAk"] = regex(text, r"B\.2\s+(\d{2}-\d{3}-\d{2})")

    data.update(extract_objek_pajak_info(text))

    data["jenis dokumen"] = regex(text, r"Jenis Dokumen\s*:\s*(.+)")
    data["Tanggal Dokumen"] = regex(text, r"Tanggal Dokumen\s*:\s*(.+)")
    data["Nomor Dokumen"] = regex(text, r"Nomor Dokumen\s*:\s*(.+)")

    data["NPWP/NIK Pemotong"] = regex(text, r"C\.1 NPWP/NIK\s*:\s*(\d+)")
    data["NITKU Pemotong"] = regex(text, r"C\.2.*?\s*:\s*(\d+)")
    data["NAMA PEMOTONG Pemotong"] = regex(text, r"C\.3 Nama Pemotong\s*:\s*(.+)")
    data["TANGGAL Pemotong"] = regex(text, r"C\.4 Tanggal\s*:\s*(.+)")
    data["NAMA PENANDATANGAN"] = regex(text, r"C\.5 Nama Penandatangan\s*:\s*(.+)")

    return data

def sanitize_filename(text):
    return re.sub(r'[\\/*?:"<>|]', "_", str(text))

def generate_filename(row, selected_cols):
    parts = [sanitize_filename(str(row.get(col, 'NA'))) for col in selected_cols]
    return prefix + "_" + "_".join(parts) + ".pdf"

st.markdown("### 🔍 Panduan Penggunaan:")
st.markdown("Aplikasi ini memungkinkan Anda mengubah nama file PDF Bukti Potong 21 secara otomatis berdasarkan data yang diekstrak dari file.")
st.markdown("1. Pilih satu atau lebih file PDF.")
st.markdown("2. Sistem akan otomatis mengekstrak isinya.")
st.markdown("3. Anda dapat memilih kolom mana saja sebagai penamaan file.")
st.markdown("4. Isikan *Custom Awalan Nama File* untuk menentukan awalan nama file, contoh: `Bukti Potong`.")
st.markdown("5. Klik tombol Rename & Download untuk mengunduh file hasil rename.")

st.markdown("### 📄 Berikut data yang berhasil diekstrak") pada tampilan berikut ini:")
    st.dataframe(df)

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
