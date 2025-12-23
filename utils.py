import os
import pandas as pd
from datetime import datetime
from barcode import Code128
from barcode.writer import ImageWriter
from pyzbar import pyzbar
from PIL import Image
import cv2

def get_base_dir():
    return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")
QR_DIR   = os.path.join(BASE_DIR, "barcode")
MASTER_FILE = os.path.join(DATA_DIR, "master.csv")
LOG_FILE    = os.path.join(DATA_DIR, "log.csv")

def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def ensure_barcode_dir():
    os.makedirs(QR_DIR, exist_ok=True)

def create_master_file():
    if not os.path.exists(MASTER_FILE):
        with open(MASTER_FILE, "w", encoding="utf-8") as f:
            f.write("id_aset,nama,kategori,kondisi,lokasi,tanggal,barcode\n")

def create_log_file():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("waktu,id_aset,aksi,detail\n")

def ensure_setup():
    ensure_data_dir()
    ensure_barcode_dir()
    create_master_file()
    create_log_file()


def load_master():
    return pd.read_csv(MASTER_FILE)

def save_master(df):
    df.to_csv(MASTER_FILE, index=False, encoding="utf-8")

def safe_new_id(raw):
    df = load_master()
    ids = df["id_aset"].astype(str).tolist()
    if raw not in ids:
        return raw
    i = 1
    while f"{raw}_{i}" in ids:
        i += 1
    return f"{raw}_{i}"


def append_log(waktu, id_aset, aksi, detail=""):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{waktu},{id_aset},{aksi},{detail}\n")


def generate_barcode(id_aset):
    ensure_barcode_dir()
    barcode = Code128(id_aset, writer=ImageWriter())
    path = os.path.join(QR_DIR, id_aset)
    barcode.save(path)
    return path + ".png"

def scan_barcode_image(img: Image.Image):
    decoded = pyzbar.decode(img)
    if not decoded:
        return None
    return decoded[0].data.decode("utf-8")


def scan_barcode_live():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        return None

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = pyzbar.decode(frame)

        for obj in decoded_objects:
            barcode_data = obj.data.decode("utf-8")

            x, y, w, h = obj.rect
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 3)
            cv2.putText(
                frame, barcode_data,
                (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2
            )
            cap.release()
            cv2.destroyAllWindows()
            return barcode_data

        cv2.imshow("Scan Barcode (ESC untuk keluar)", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()
    return None

