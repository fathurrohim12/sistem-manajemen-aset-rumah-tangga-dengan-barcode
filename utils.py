import os
import pandas as pd
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder tempat utils.py
DATA_DIR = os.path.join(BASE_DIR, "data")
MASTER_FILE = os.path.join(DATA_DIR, "master.csv")
LOG_FILE    = os.path.join(DATA_DIR, "log.csv")

#membuat master.csv dan log.csv kalau belum ada
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
#menyimpan aktivitas RUD
def load_master():
    return pd.read_csv(MASTER_FILE)

def save_master(df):
    df.to_csv(MASTER_FILE, index=False, encoding="utf-8")
    print(f"master.csv berhasil disimpan! Total aset: {len(df)}")

def append_log(waktu, id_aset, aksi, detail=""):
    line = f"{waktu},{id_aset},{aksi},{detail}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"Log ditulis: {line.strip()}")

