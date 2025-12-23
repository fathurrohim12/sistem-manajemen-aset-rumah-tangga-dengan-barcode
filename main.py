import streamlit as st
import pandas as pd
from datetime import datetime
from PIL import Image
import os
from streamlit_option_menu import option_menu

from utils import (
    ensure_setup, load_master, save_master, append_log,
    generate_barcode,  scan_barcode_live,scan_barcode_image,
    safe_new_id,
    DATA_DIR, QR_DIR
)

ensure_setup()

st.set_page_config(page_title="Manajemen Aset Barcode", layout="wide")

# CSS umum
st.markdown("""
<style>

/* ================= GLOBAL ================= */
html, body, [class*="css"]  {
    font-family: 'Poppins', sans-serif;
}

.main {
    background: linear-gradient(135deg, #f4f6fb 0%, #eef1f7 100%) !important;
}

/* ================= SIDEBAR ================= */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
    padding-top: 20px;
}

[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

.menu-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 20px;
    padding: 12px 16px;
    border-radius: 14px;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(6px);
}

/* ================= MENU ITEM ================= */
.nav-link {
    border-radius: 14px !important;
    padding: 12px 18px !important;
    margin: 6px 8px !important;
    transition: all 0.25s ease;
}

.nav-link:hover {
    background: rgba(255,255,255,0.18) !important;
    transform: translateX(6px);
}

.nav-link-selected {
    background: linear-gradient(135deg, #ffffff33, #ffffff11) !important;
    box-shadow: 0 8px 20px rgba(0,0,0,0.25);
}

/* ================= HEADER ================= */
h1, h2, h3 {
    color: #1f3c88 !important;
    font-weight: 700;
}

h4 {
    color: #4e73df !important;
}

/* ================= CARD ================= */
.stMetric, .stDataFrame, .stAlert {
    background: white;
    border-radius: 18px;
    padding: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

/* ================= BUTTON ================= */
.stButton>button {
    background: linear-gradient(135deg, #4e73df, #224abe);
    color: white;
    font-weight: 600;
    border-radius: 14px;
    padding: 10px 24px;
    border: none;
    transition: all 0.25s ease;
}

.stButton>button:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(78,115,223,0.45);
}

/* ================= INPUT ================= */
.stTextInput input,
.stSelectbox div[data-baseweb="select"] {
    border-radius: 14px !important;
    border: 1px solid #d6d9e6 !important;
    padding: 10px;
}

/* ================= DATAFRAME ================= */
[data-testid="stDataFrame"] {
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
}

/* ================= UPLOADER ================= */
.stFileUploader {
    background: white;
    border-radius: 18px;
    padding: 16px;
    border: 2px dashed #4e73df55;
}

/* ================= DIVIDER ================= */
hr {
    margin: 30px 0;
    border: none;
    height: 2px;
    background: linear-gradient(to right, transparent, #4e73df55, transparent);
}

</style>
""", unsafe_allow_html=True)

if "login" not in st.session_state:
    st.session_state.login = False
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

    st.stop()  

#CSS(menu utama)
st.markdown("""
<style>

/* ================= MENU TITLE (SIDEBAR) ================= */
.menu-title {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #ffffff;
    font-family: 'Poppins', sans-serif;

    padding: 14px 18px;
    margin-bottom: 22px;

    border-radius: 16px;

    /* glassmorphism */
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);

    /* shadow halus */
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
}



</style>
""", unsafe_allow_html=True)
#CSS option menu
st.markdown("""
<style>
/* SIDEBAR UTAMA */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #3f63d8, #2b4bb8);
    padding-top: 18px;
}

/* hilangkan padding default */
section[data-testid="stSidebar"] > div {
    padding: 12px;
}
</style>
""", unsafe_allow_html=True)

#CSS TAMPILAN MENU
with st.sidebar:
    st.markdown('<div class="menu-title">☰  MENU UTAMA</div>', unsafe_allow_html=True)

    menu = option_menu(
    None,
    [
        "Dashboard",
        "Tambah Aset",
        "Lihat Aset",
        "Update Kondisi",
        "Hapus Aset",
        "Scan Barcode",
        "Scan gambar",
        "Log Aktivitas",
        "Log out"
    ],
    icons=[
        "speedometer2",
        "plus-circle",
        "card-list",
        "arrow-repeat",
        "trash",
        "qr-code-scan",
        "image",
        "journal-text",
        "box-arrow-right"
    ],
    default_index=0,
    styles={
        # container menu
        "container": {
            "padding": "14px",
            "background": "linear-gradient(180deg, #3f63d8, #2b4bb8)",
            "border-radius": "26px",
        },

        # icon menu
        "icon": {
            "color": "white",
            "font-size": "20px",
        },

        # menu item (SEMUA)
        "nav-link": {
            "font-size": "16px",
            "font-weight": "500",
            "color": "white",
            "padding": "16px 22px",
            "margin": "10px 6px",
            "border-radius": "22px",
            "background": "rgba(255,255,255,0.12)",
            "transition": "all 0.25s ease",
        },

        # hover menu
        "nav-link-hover": {
            "background": "rgba(255,255,255,0.25)",
            "transform": "translateX(6px)",
        },

        # menu aktif
        "nav-link-selected": {
            "background": "linear-gradient(135deg, #ffffff55, #ffffff22)",
            "font-weight": "600",
            "box-shadow": "0 14px 32px rgba(0,0,0,0.35)",
        },
    },
)


# DASHBOARD
if menu == "Dashboard":
    st.header("Dashboard")

    df = load_master()
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("""
        <div style="
            background:white;
            border-radius:18px;
            padding:20px;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);
        ">
            <h4>Total Aset</h4>
            <h1 style="margin:0;color:#1f3c88;">{}</h1>
        </div>
        """.format(len(df)), unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div style="
            background:white;
            border-radius:18px;
            padding:20px;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);
        ">
            <h4>Kondisi Baik</h4>
            <h1 style="margin:0;color:#2e59d9;">{}</h1>
        </div>
        """.format((df["kondisi"] == "baik").sum() if not df.empty else 0),
        unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div style="
            background:white;
            border-radius:18px;
            padding:20px;
            box-shadow:0 10px 25px rgba(0,0,0,0.08);
        ">
            <h4>Aset Bermasalah</h4>
            <h1 style="margin:0;color:#c0392b;">{}</h1>
        </div>
        """.format((df["kondisi"].isin(["rusak","hilang"])).sum() if not df.empty else 0),
        unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Distribusi Kondisi Aset")
    if df.empty:
        st.info("Belum ada data aset.")
    else:
        import matplotlib.pyplot as plt

        kondisi_count = df["kondisi"].value_counts()
        labels = ["baik", "rusak", "hilang"]
        colors = {
            "baik": "#2e59d9",     # biru
            "rusak": "#e74c3c",    # merah
            "hilang": "#2c2c2c"    # hitam
        }

        values = [kondisi_count.get(k, 0) for k in labels]
        bar_colors = [colors[k] for k in labels]

        fig, ax = plt.subplots(figsize=(5, 3))

        ax.bar(labels, values)

        for bar, color in zip(ax.patches, bar_colors):
            bar.set_color(color)

        ax.set_ylabel("Jumlah Aset")
        ax.set_xlabel("Kondisi")
        ax.set_title("Distribusi Kondisi Aset")

        st.pyplot(fig)

elif menu == "Tambah Aset":
    st.header("Tambah Aset")

    st.markdown("""
    <div style="
        background:white;
        border-radius:20px;
        padding:28px;
        max-width:800px;
        box-shadow:0 14px 35px rgba(0,0,0,0.10);
    ">
    """, unsafe_allow_html=True)

    with st.form("form_tambah"):
        col1, col2 = st.columns(2)

        with col1:
            raw_id = st.text_input("ID Aset")
            nama = st.text_input("Nama Aset")
            kategori = st.text_input("Kategori")

        with col2:
            lokasi = st.text_input("Lokasi")
            kondisi = st.selectbox(
                "Kondisi Aset",
                ["baik", "rusak", "hilang"]
            )

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Simpan Aset")

    st.markdown("</div>", unsafe_allow_html=True)

    if submit:
        if raw_id.strip() == "" or nama.strip() == "":
            st.error("ID dan Nama Aset wajib diisi.")
        else:
            id_aset = safe_new_id(raw_id.strip())
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            qr_path = generate_barcode(id_aset)


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

            st.success("Aset berhasil ditambahkan!")

            st.image(qr_path, width=180)
            with open(qr_path, "rb") as f:
                st.download_button(
                    "⬇Download QR Code",
                    f,
                    file_name=f"{id_aset}.png"
                )

elif menu == "Lihat Aset":
    st.header("Daftar Aset")

    df = load_master()

    if df.empty:
        st.info("Belum ada data aset.")
    else:
        keyword = st.text_input("Cari aset (ID / Nama / Lokasi / Kondisi)")

        if keyword:
            df = df[
                df["id_aset"].astype(str).str.contains(keyword, case=False) |
                df["nama"].str.contains(keyword, case=False) |
                df["lokasi"].str.contains(keyword, case=False) |
                df["kondisi"].str.contains(keyword, case=False)
            ]

        df = df.sort_values("tanggal", ascending=False)

        st.dataframe(
            df,
            use_container_width=True
        )

elif menu == "Update Kondisi":
    st.header("Update Kondisi Aset")
    df = load_master()

    if df.empty:
        st.info("Tidak ada aset.")
    else:
        keyword = st.text_input("Cari aset (ID atau Nama Aset)")

        if keyword:
            df_filter = df[
                df["id_aset"].astype(str).str.contains(keyword, case=False) |
                df["nama"].str.contains(keyword, case=False)
            ]
        else:
            df_filter = df

        if df_filter.empty:
            st.warning("Aset tidak ditemukan.")
        else:
            id_aset = st.selectbox(
                "Pilih aset:",
                df_filter["id_aset"].tolist()
            )

            row = df[df["id_aset"] == id_aset].iloc[0]

            st.info(
                f"Aset: **{row['nama']}**  \n"
                f"Lokasi: **{row['lokasi']}**  \n"
                f"Kondisi saat ini: **{row['kondisi']}**"
            )

            new_kondisi = st.selectbox(
                "Kondisi Baru:",
                ["baik", "rusak", "hilang"],
                index=["baik", "rusak", "hilang"].index(row["kondisi"])
                if row["kondisi"] in ["baik", "rusak", "hilang"] else 0
            )

            if st.button("Simpan Perubahan", type="primary"):
                df.loc[df["id_aset"] == id_aset, "kondisi"] = new_kondisi
                save_master(df)

                append_log(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    id_aset,
                    "update_kondisi",
                    f"{row['kondisi']} → {new_kondisi}"
                )

                st.success("Kondisi aset berhasil diperbarui!")

elif menu == "Hapus Aset":
    st.header("Hapus Aset")
    df = load_master()

    if df.empty:
        st.info("Tidak ada aset.")
    else:
        keyword = st.text_input("Cari aset (ID atau Nama Aset)")

        if keyword:
            df_filter = df[
                df["id_aset"].astype(str).str.contains(keyword, case=False) |
                df["nama"].str.contains(keyword, case=False)
            ]
        else:
            df_filter = df

        if df_filter.empty:
            st.warning("Aset tidak ditemukan.")
        else:
            id_aset = st.selectbox(
                "Pilih aset yang akan dihapus:",
                df_filter["id_aset"].tolist()
            )

            row = df[df["id_aset"] == id_aset].iloc[0]

            st.warning(
                f"Anda akan menghapus aset **{row['nama']}** "
                f"di lokasi **{row['lokasi']}**."
            )

            if st.button("Hapus Aset", type="primary"):
                new_df = df[df["id_aset"] != id_aset]
                save_master(new_df)
                if "barcode" in row and os.path.exists(row["barcode"]):
                    os.remove(row["barcode"])

                append_log(
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    id_aset,
                    "hapus",
                    f"{row['nama']}, {row['lokasi']}"
                )

                st.success("Aset berhasil dihapus!")

elif menu == "Scan Barcode":
    st.header("Scan Barcode Aset (Live Camera)")

    if st.button("Mulai Scan Barcode"):
        hasil = scan_barcode_live()

        if hasil:
            st.success(f"ID Aset Terbaca: {hasil}")

            df = load_master()
            data = df[df["id_aset"] == hasil]

            if data.empty:
                st.error("Aset tidak ditemukan di master.csv")
            else:
                nama_barang = data.iloc[0]["nama"]
                kategori = data.iloc[0]["kategori"]
                lokasi = data.iloc[0]["lokasi"]
                kondisi = data.iloc[0]["kondisi"]

                st.subheader(" Data Aset")
                st.write(f"**Nama Barang :** {nama_barang}")
                st.write(f"**Kategori :** {kategori}")
                st.write(f"**Lokasi :** {lokasi}")
                st.write(f"**Kondisi :** {kondisi}")
        else:
            st.warning("Scan dibatalkan / barcode tidak terbaca")

    st.divider()

elif menu == "Scan gambar":
    st.subheader("Scan dari Gambar (Upload)")

    uploaded = st.file_uploader("Upload gambar barcode:")

    if uploaded:
        img = Image.open(uploaded).convert("RGB")
        st.image(img, width=250)

        hasil = scan_barcode_image(img)  

        if hasil:
            st.success(f"ID Terbaca: {hasil}")
            data = load_master()
            row = data[data["id_aset"] == hasil]

            if row.empty:
                st.error("Tidak ada aset dengan ID tersebut.")
            else:
                st.write(row)
        else:
            st.error("Gagal membaca barcode.")

elif menu == "Log Aktivitas":
    st.header("Log Aktivitas")

    df = pd.read_csv(f"{DATA_DIR}/log.csv")

    if df.empty:
        st.info("Belum ada log.")
    else:
        st.dataframe(df.sort_values("waktu", ascending=False), use_container_width=True)

elif menu == "Log out":
    st.session_state.login = False
    st.rerun()

