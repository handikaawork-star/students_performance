# Menjalankan Prototype Streamlit

Prototype prediksi risiko dropout mahasiswa Jaya Jaya Institut ada di `app.py`.

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
1. Isi form: profil, keuangan, dan hasil semester 1.
2. Klik **Prediksi**.
3. Aplikasi menampilkan skor risiko, level risiko (Tinggi, Sedang, Rendah), saran tindakan, dan faktor yang memengaruhi skor.

**Tab "Banyak mahasiswa (CSV)"**
1. Unggah CSV dengan pemisah `;` dan kolom yang sama seperti `data/students_performance.csv`.
2. Lihat jumlah mahasiswa per level risiko dan tabel yang diurutkan dari risiko tertinggi.
3. Unduh hasilnya sebagai CSV.

## Level risiko

| Skor | Level |
|---|---|
| >= 0,5 | Tinggi |
| 0,3 sampai < 0,5 | Sedang |
| < 0,3 | Rendah |

Skor dipakai untuk mengurutkan prioritas pendampingan, bukan probabilitas sebenarnya.

## Prediksi lewat command line (opsional)

```bash
python main.py
python main.py --input data/mahasiswa_baru.csv --output data/hasil.csv --top 20
```

## Deploy ke Streamlit Community Cloud

1. Push proyek ke repository GitHub publik. Pastikan `app.py`, `requirements.txt`, `model/`, dan `data/students_performance.csv` ikut ter-commit.
2. Buka <https://share.streamlit.io> dan login dengan akun GitHub.
3. Klik **Create app**, pilih repository dan branch, lalu isi **Main file path** dengan `app.py`.
4. Klik **Deploy**.

Link prototype: _isi setelah deploy_

## Pemecahan masalah

| Masalah | Solusi |
|---|---|
| `FileNotFoundError: model/...` | Jalankan dari root proyek, bukan dari folder lain |
| Model gagal dimuat | Samakan versi scikit-learn dengan `requirements.txt` (`1.9.1`) |
| `source .venv/bin/activate` gagal di WSL | `.venv` dibuat di Windows. Buat venv baru di WSL atau jalankan dari PowerShell |
