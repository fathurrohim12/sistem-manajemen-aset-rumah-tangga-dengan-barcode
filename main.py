import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os

from utils import (
    ensure_setup, load_master, save_master, append_log,
    generate_qr, scan_qr_image, safe_new_id,
    DATA_DIR, QR_DIR
)

# Setup awal
ensure_setup()

# LOGIN SEDERHANA

if "login" not in st.session_state:
    st.session_state.login = False

# Akun dummy (bisa kamu ganti)
USERNAME = "admin"
PASSWORD = "1"

if not st.session_state.login:
    st.title("Login Sistem Aset")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.login = True
            st.success("Login berhasil!")
            st.rerun()
        else:
            st.error("Username atau password salah!")

    st.stop()  # menghentikan akses ke sistem sebelum login

#TAMPILAN MENU
with st.sidebar:
    st.markdown('<div class="menu-title">☰  MENU UTAMA</div>', unsafe_allow_html=True)

    menu = option_menu(
        None,       # hilangkan judul bawaan
        ["Dashboard", "Tambah Aset", "Lihat Aset", "Update Kondisi",
         "Hapus Aset", "Scan Barcode", "Log Aktivitas", "Log out"],
        icons=["speedometer2", "plus-circle", "card-list", "arrow-repeat",
               "trash", "qr-code-scan", "journal-text", "box-arrow-right"],
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "#4e73df"},
            "icon": {"color": "white", "font-size": "18px"},
            "nav-link": {
                "color": "white",
                "font-size": "16px",
                "text-align": "left",
                "margin": "3px",
            },
            "nav-link-selected": {"background-color": "#2e59d9"},
        },
    )


# DASHBOARD
if menu == "Dashboard":
    st.header("Dashboard")
    df = load_master()

    st.metric("Total Aset", len(df))

    if len(df) > 0:
        st.subheader("Distribusi Kondisi")
        st.bar_chart(df["kondisi"].value_counts())
    else:
        st.info("Belum ada data aset.")

# TAMBAH ASET

elif menu == "Tambah Aset":
    st.header("Tambah Aset")
    with st.form("form_tambah"):
        raw_id = st.text_input("Id Aset:")
        nama = st.text_input("Nama Aset:")
        kategori = st.text_input("Kategori:")
        kondisi = st.selectbox("Kondisi:", ["baik", "rusak", "hilang"])
        lokasi = st.text_input("Lokasi:")
        submit = st.form_submit_button("Simpan")

    if submit:
        if raw_id is None or raw_id.strip() == "" or nama.strip() == "":
            st.error("ID dan nama wajib diisi!")
        else:
            id_aset = safe_new_id(raw_id.strip())
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            qr_path = generate_qr(id_aset)

            df = load_master()
            new = {
                "id_aset": id_aset,
                "nama": nama,
                "kategori": kategori,
                "kondisi": kondisi,
                "lokasi": lokasi,
                "tanggal": waktu,
                "barcode": qr_path.replace("\\", "/")
            }
            df = pd.concat([df, pd.DataFrame([new])], ignore_index=True)
            save_master(df)

            append_log(waktu, id_aset, "tambah", f"{nama}, {lokasi}")

            st.success(f"Aset {id_aset} berhasil ditambahkan!")
            st.image(qr_path, width=200)

            with open(qr_path, "rb") as f:
                st.download_button("Download QR", f, file_name=f"{id_aset}.png")

# LIHAT ASET

elif menu == "Lihat Aset":
    st.header("Daftar Aset")
    df = load_master()

    if df.empty:
        st.info("Belum ada aset.")
    else:
        q = st.text_input("Cari aset:")
        if q:
            df = df[df.apply(lambda r: q.lower() in " ".join(r.astype(str)).lower(), axis=1)]

        st.dataframe(df, use_container_width=True)

# UPDATE KONDISI

elif menu == "Update Kondisi":
    st.header("Update Kondisi Aset")
    df = load_master()

    if df.empty:
        st.info("Tidak ada aset.")
    else:
        id_aset = st.selectbox("Pilih aset:", df["id_aset"].tolist())
        row = df[df["id_aset"] == id_aset].iloc[0]

        st.write("Kondisi saat ini:", row["kondisi"])
        new_kondisi = st.selectbox("Kondisi baru:", ["baik", "rusak", "hilang"])

        if st.button("Simpan Perubahan"):
            df.loc[df["id_aset"] == id_aset, "kondisi"] = new_kondisi
            save_master(df)

            append_log(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                id_aset,
                "update_kondisi",
                f"{row['kondisi']} → {new_kondisi}"
            )

            st.success("Kondisi berhasil diperbarui!")

# HAPUS ASET

elif menu == "Hapus Aset":
    st.header("Hapus Aset")
    df = load_master()

    if df.empty:
        st.info("Tidak ada aset.")
    else:
        id_aset = st.selectbox("Pilih aset yang akan dihapus:", df["id_aset"].tolist())

        row = df[df["id_aset"] == id_aset].iloc[0]
        st.warning(f"Anda akan menghapus aset **{row['nama']}** di lokasi **{row['lokasi']}**.")

        if st.button("Hapus Aset", type="primary"):
            # Hapus dari dataframe
            new_df = df[df["id_aset"] != id_aset]
            save_master(new_df)

            # Hapus barcode jika ada
            if os.path.exists(row["barcode"]):
                os.remove(row["barcode"])

            # Log
            append_log(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                id_aset,
                "hapus",
                f"{row['nama']}, {row['lokasi']}"
            )

            st.success("Aset berhasil dihapus!")

# LOG
elif menu == "Log Aktivitas":
    st.header("Log Aktivitas")

    df = pd.read_csv(f"{DATA_DIR}/log.csv")

    if df.empty:
        st.info("Belum ada log.")
    else:
        st.dataframe(df.sort_values("waktu", ascending=False), use_container_width=True)

#log out
elif menu == "Log out":
    st.session_state.login = False
    st.rerun()

