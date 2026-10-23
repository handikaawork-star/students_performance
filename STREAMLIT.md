# Menjalankan Prototype Streamlit

Prototype prediksi risiko dropout mahasiswa Jaya Jaya Institut ada di `app.py`. Model dilatih hanya pada mahasiswa Dropout (1) dan Graduate (0); mahasiswa Enrolled menjadi sasaran prediksi.

## Prasyarat

- Python (versi sesuai `.python-version`)
- Folder proyek lengkap, terutama `app.py`, `model/`, dan `data/students_performance.csv`

## Cara 1: Memakai uv

```bash
uv sync
uv run streamlit run app.py
```

## Cara 2: Memakai pip

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Mengakses aplikasi

Browser terbuka otomatis di <http://localhost:8501>. Jika tidak terbuka, buka alamat itu secara manual. Hentikan aplikasi dengan `Ctrl+C`.

## Cara memakai

**Tab "Satu mahasiswa"**
1. Isi form lengkap: profil, data pendaftaran dan keluarga, keuangan, hasil semester 1, dan kondisi makro. Semua kolom wajib diisi dengan data aktual mahasiswa; tidak ada nilai awal maupun nilai pengganti (median), dan prediksi tidak jalan bila ada yang kosong.
2. Klik **Prediksi**.
3. Aplikasi menampilkan skor risiko, level risiko (Tinggi, Sedang, Rendah), saran tindakan, dan faktor yang memengaruhi skor.

**Tab "Banyak mahasiswa (CSV)"**
1. Unggah CSV dengan pemisah `;` dan kolom yang sama seperti `data/students_performance.csv`.
2. Lihat jumlah mahasiswa per level risiko dan tabel yang diurutkan dari risiko tertinggi.
3. Unduh hasilnya sebagai CSV.

Tombol **Atau coba dengan mahasiswa Enrolled dari dataset** menjalankan prediksi pada 794 mahasiswa Enrolled, yaitu data yang tidak dipakai saat training.

## Level risiko

| Skor | Level |
|---|---|
| >= 0,5 | Tinggi |
| 0,3 sampai < 0,5 | Sedang |
| < 0,3 | Rendah |

Skor dipakai untuk mengurutkan prioritas pendampingan, bukan probabilitas sebenarnya.

Link prototype: [Prototype](https://studentsperformance-qwerty.streamlit.app/)

