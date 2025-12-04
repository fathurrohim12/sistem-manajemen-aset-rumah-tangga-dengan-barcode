# main.py
import streamlit as st
import pandas as pd
from datetime import datetime
import os

from utils import (
    ensure_setup, load_master, save_master, append_log,
    generate_qr, scan_qr_image, safe_new_id,
    DATA_DIR, QR_DIR
)

# Setup awal
ensure_setup()

st.set_page_config(page_title="Manajemen Aset Barcode", layout="wide")
st.title("📦 Sistem Manajemen Aset Rumah Tangga dengan Barcode")

menu = st.sidebar.selectbox(
    "Menu",
    ["Dashboard", "Tambah Aset", "Lihat Aset", "Update Kondisi",
     "Hapus Aset", "Scan Barcode", "Download CSV", "Log"]
)


# DASHBOARD
if menu == "Dashboard":
    st.header("📊 Dashboard")
    df = load_master()

    st.metric("Total Aset", len(df))

    if len(df) > 0:
        st.subheader("Distribusi Kondisi")
        st.bar_chart(df["kondisi"].value_counts())
    else:
        st.info("Belum ada data aset.")

# TAMBAH ASET
elif menu == "Tambah Aset":
    st.header("➕ Tambah Aset")

    with st.form("form_tambah"):
        raw_id = st.text_input(
            "ID Aset:",
            value=f"AS{datetime.now().strftime('%y%m%d%H%M%S')}"
        )
        nama = st.text_input("Nama Aset:")
        kategori = st.text_input("Kategori:")
        kondisi = st.selectbox("Kondisi:", ["baik", "rusak", "hilang"])
        lokasi = st.text_input("Lokasi:")
        submit = st.form_submit_button("Simpan")

    if submit:
        if raw_id.strip() == "" or nama.strip() == "":
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
    st.header("📋 Daftar Aset")
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
    st.header("🔧 Update Kondisi Aset")
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
    st.header("🗑 Hapus Aset")
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

          