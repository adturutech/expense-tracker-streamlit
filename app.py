import streamlit as st
import pandas as pd
from datetime import date
from db import (
    init_db, insert_transaction, fetch_transactions,
    delete_transaction, update_transaction, get_transaction, list_categories
)


def format_rupiah(amount):
    return f"Rp {amount:,.0f}".replace(",", ".")

st.set_page_config(page_title="Pencatat Pengeluaran", layout="wide")
init_db()

st.title("💸 Aplikasi Pencatat Pengeluaran & Pemasukan ")

col1, col2 = st.columns([1, 2])

with col1:
    st.header("Tambah Transaksi Baru")

    with st.form("add_tx", clear_on_submit=True):
        tx_date = st.date_input("Tanggal", value=date.today())
        ttype = st.selectbox("Jenis", ["pengeluaran", "pemasukan"])
        existing_categories = list_categories()
        category = st.text_input("Kategori", value=existing_categories[0] if existing_categories else "Lainnya")
        
        amount = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
        desc = st.text_area("Catatan", "", height=80)

        submitted = st.form_submit_button("Tambah")
        if submitted:
            if amount <= 0:
                st.error("Jumlah harus lebih dari 0")
            else:
                insert_transaction(
                    tx_date.isoformat(),
                    int(amount),
                    category.strip(),
                    "expense" if ttype == "pengeluaran" else "income",
                    desc.strip()
                )
                st.success("Transaksi berhasil ditambahkan!")
                st.rerun()

    st.markdown("---")
    st.header("Edit / Hapus Transaksi")

    txs_all = fetch_transactions(limit=1000)
    if txs_all:
        df_all = pd.DataFrame(txs_all)
        df_all['label'] = df_all.apply(
            lambda r: f"{r['id']} — {r['date']} — {r['type']} — {format_rupiah(r['amount'])} ({r['category']})",
            axis=1
        )
        selection = st.selectbox("Pilih transaksi", options=[""] + df_all['label'].tolist())

        if selection:
            selected_id = int(selection.split(" — ")[0])
            tx = get_transaction(selected_id)

            st.subheader("Edit Transaksi")
            with st.form("edit_tx"):
                edit_date = st.date_input("Tanggal", value=pd.to_datetime(tx['date']).date())
                edit_type = st.selectbox(
                    "Jenis",
                    ["pengeluaran", "pemasukan"],
                    index=0 if tx['type'] == "expense" else 1
                )
                edit_category = st.text_input("Kategori", value=tx['category'])
                edit_amount = st.number_input("Jumlah (Rp)", min_value=0, value=int(tx['amount']), step=1000)
                edit_desc = st.text_area("Catatan", value=tx['description'] or "")

                edit_sub = st.form_submit_button("Simpan Perubahan")
                if edit_sub:
                    update_transaction(
                        selected_id,
                        edit_date.isoformat(),
                        int(edit_amount),
                        edit_category.strip(),
                        "expense" if edit_type == "pengeluaran" else "income",
                        edit_desc.strip()
                    )
                    st.success("Transaksi berhasil diperbarui!")
                    st.rerun()

            if st.button("Hapus Transaksi Ini"):
                delete_transaction(selected_id)
                st.success("Transaksi dihapus!")
                st.rerun()
    else:
        st.info("Belum ada transaksi.")

# ============================================================
# KANAN — Daftar, Filter, Summary
# ============================================================
with col2:
    st.header("Daftar Transaksi")

    # Filter
    c1, c2, c3 = st.columns(3)
    with c1:
        start_date = st.date_input("Dari Tanggal", value=date(2000, 1, 1))
    with c2:
        end_date = st.date_input("Sampai Tanggal", value=date.today())
    with c3:
        cats = ["Semua"] + list_categories()
        chosen_cat = st.selectbox("Kategori", cats)

    limit = st.number_input("Jumlah Baris Maksimal", min_value=10, max_value=5000, value=200)

    # Fetch
    txs = fetch_transactions(
        limit=int(limit),
        start_date=start_date.isoformat(),
        end_date=end_date.isoformat(),
        category=None if chosen_cat == "Semua" else chosen_cat
    )

    if txs:
        df = pd.DataFrame(txs)
        df['date'] = pd.to_datetime(df['date'])
        df_display = df.copy()
        df_display['date'] = df_display['date'].dt.date
        df_display['amount'] = df_display['amount'].apply(lambda x: format_rupiah(int(x)))

        st.dataframe(df_display.sort_values(by="date", ascending=False), use_container_width=True)

        # Summary
        st.markdown("### Ringkasan")
        total_income = df[df['type'] == 'income']['amount'].sum()
        total_expense = df[df['type'] == 'expense']['amount'].sum()

        colA, colB, colC = st.columns(3)
        colA.metric("Total Pemasukan", format_rupiah(total_income))
        colB.metric("Total Pengeluaran", format_rupiah(total_expense))
        colC.metric("Saldo", format_rupiah(total_income - total_expense))

        # Chart
        st.markdown("### Grafik Bulanan")

        df_month = df.copy()
        df_month["month"] = df_month["date"].dt.to_period("M").dt.to_timestamp()
        monthly = df_month.groupby(["month", "type"])["amount"].sum().unstack(fill_value=0)

        st.bar_chart(monthly)

        # Export CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Unduh CSV", data=csv, file_name="data_keuangan.csv", mime="text/csv")

    else:
        st.info("Tidak ada transaksi ditemukan dengan filter ini.")
