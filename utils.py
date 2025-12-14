import os
import pandas as pd
from datetime import datetime
from barcode import Code128
from barcode.writer import ImageWriter
from pyzbar import pyzbar
from PIL import Image

# folder tempat utils.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  
DATA_DIR = os.path.join(BASE_DIR, "data")
QR_DIR   = os.path.join(BASE_DIR, "barcode")
MASTER_FILE = os.path.join(DATA_DIR, "master.csv")
LOG_FILE    = os.path.join(DATA_DIR, "log.csv")

#Membuat folder dan file seperti master.csv & log.csv kalau belum ada.
def ensure_setup():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(QR_DIR, exist_ok=True)
    print(f"DATA DISIMPAN DI: {DATA_DIR}")
    print(f"BARCODE DISIMPAN DI: {QR_DIR}")

    if not os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "w", encoding="utf-8") as f:
            f.write("id_aset,nama,kategori,kondisi,lokasi,tanggal,barcode\n")

    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("waktu,id_aset,aksi,detail\n")

#baca dan simpan data
def load_master():
    return pd.read_csv(MASTER_FILE)

def save_master(df):
    df.to_csv(MASTER_FILE, index=False, encoding="utf-8")
    print(f"master.csv berhasil disimpan! Total aset: {len(df)}")

#Mencatat aktivitas CRUD
def append_log(waktu, id_aset, aksi, detail=""):
    line = f"{waktu},{id_aset},{aksi},{detail}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"Log ditulis: {line.strip()}")

#membuat gambar barcode
def generate_qr(id_aset):
    os.makedirs(QR_DIR, exist_ok=True)
    file_path = os.path.join(QR_DIR, f"{id_aset}.png")
    barcode = Code128(id_aset, writer=ImageWriter())
    barcode.save(os.path.splitext(file_path)[0])
    full_path = os.path.abspath(file_path)
    print(f"BARCODE BERHASIL DISIMPAN → {full_path}")
    return file_path

#membuat id otomatis
def safe_new_id(raw):
    df = load_master()
    ids = df["id_aset"].astype(str).tolist()
    if raw not in ids: return raw
    i = 1
    while f"{raw}_{i}" in ids: i += 1
    return f"{raw}_{i}"

#membaca barcode dari gambar
def scan_qr_image(img: Image.Image):
    decoded = pyzbar.decode(img)
    if not decoded: return None
    return decoded[0].data.decode("utf-8")
