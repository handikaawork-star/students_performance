# Proyek Akhir: Menyelesaikan Permasalahan Perusahaan Edutech

## Business Understanding

Jaya Jaya Institut adalah institusi pendidikan tinggi yang menyelenggarakan berbagai program studi. Salah satu tantangan terbesarnya adalah banyak mahasiswa yang tidak menyelesaikan studi (*dropout*). Pada data yang dianalisis, **32,1% dari 4.424 mahasiswa berstatus Dropout**, atau hampir 1 dari 3 mahasiswa.

Dropout merugikan mahasiswa dan institusi: pendapatan uang kuliah hilang, tingkat kelulusan turun, dan reputasi program studi terpengaruh. Selama ini institusi baru mengetahui seorang mahasiswa bermasalah setelah ia berhenti, padahal pendampingan paling efektif dilakukan sebelum itu terjadi.

### Permasalahan Bisnis

1. Faktor apa saja yang paling berhubungan dengan dropout?
2. Kelompok atau program studi mana yang paling rentan?
3. Bagaimana mengenali mahasiswa berisiko dropout sedini mungkin agar dapat didampingi?
4. Bagaimana institusi memantau performa dan risiko dropout mahasiswa secara berkelanjutan?

### Cakupan Proyek

1. **Analisis data (EDA)** untuk mengidentifikasi faktor yang berhubungan dengan dropout (`notebook.ipynb`).
2. **Business dashboard** di Metabase untuk memantau dropout rate dan faktor penyebabnya.
3. **Model machine learning** yang memprediksi risiko dropout setelah semester 1 selesai, dengan model yang dibandingkan, di-tuning, dan dievaluasi pada data uji.
4. **Prototype Streamlit** agar staf institusi dapat memakai model tanpa menulis kode.
5. **Kesimpulan dan rekomendasi action items** untuk menurunkan dropout.

Di luar cakupan: menentukan penyebab sebab-akibat dropout, dan memakai informasi semester 2 (model sengaja hanya memakai data sampai akhir semester 1 supaya dapat dipakai lebih awal).

### Persiapan

Sumber data: `data/students_performance.csv`. Data berisi 4.424 mahasiswa dengan 36 fitur (demografi, ekonomi, jalur pendaftaran, dan kinerja semester 1-2) serta target `Status` (Dropout, Enrolled, Graduate). Tidak ada missing value maupun baris duplikat.

Setup environment:

Dengan `uv`:
```bash
uv sync
```

Atau dengan pip:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Untuk dashboard dibutuhkan juga Docker dan Docker Compose.

Struktur proyek:

| Berkas | Fungsi |
|---|---|
| `notebook.ipynb` | Seluruh proses: data understanding, preparation, modeling, evaluation |
| `app.py` | Prototype Streamlit |
| `model/` | Model terlatih dan berkas pendukungnya |
| `docker-compose.yml`, `sql/`, `data/students_dashboard.csv`, `metabase.db.mv.db` | Dashboard Metabase |
| `main.py` | Prediksi lewat command line (opsional) |
| `METABASE.md`, `STREAMLIT.md` | Panduan lengkap dashboard dan prototype |

## Business Dashboard

Dashboard **Monitoring Dropout Mahasiswa - Jaya Jaya Institut** dibuat dengan Metabase. Isinya:

- Ringkasan: total mahasiswa, dropout rate, persentase lulus, dan jumlah mahasiswa aktif berisiko tinggi.
- Komposisi status mahasiswa.
- Dropout rate menurut usia, kondisi keuangan (uang kuliah, utang, beasiswa), program studi, gender, dan kelas.
- Rata-rata mata kuliah lulus per status.
- Sinyal dini: dropout rate mahasiswa dengan nilai semester 1 kosong.
- Level risiko mahasiswa yang masih aktif.

Semua visual dapat difilter berdasarkan program studi dan jenis kelamin.

Cara mengakses:

```bash
docker compose up -d
```

Tunggu sekitar 1 menit, lalu buka <http://localhost:3000>. Dashboard sudah termuat otomatis.

| | |
|---|---|
| Email | `root@mail.com` |
| Password | `root123` |

Berkas `metabase.db.mv.db` adalah ekspor database Metabase. Detail lengkap ada di [METABASE.md](METABASE.md).

## Menjalankan Sistem Machine Learning

Prototype Streamlit memprediksi risiko dropout seorang mahasiswa (lewat form) atau banyak mahasiswa sekaligus (lewat unggah CSV), lengkap dengan level risiko dan faktor yang memengaruhi skor.

**Link prototype:** <https://studentsperformance-qwerty.streamlit.app/>

Menjalankan secara lokal:

```bash
uv run streamlit run app.py
# atau, setelah pip install -r requirements.txt:
streamlit run app.py
```

Buka <http://localhost:8501>. Panduan lengkap ada di [STREAMLIT.md](STREAMLIT.md).

## Conclusion

Sekitar 32% mahasiswa Jaya Jaya Institut dropout. Analisis menunjukkan dropout sangat berkaitan dengan tiga hal:

1. **Kinerja akademik semester 1 adalah sinyal terkuat.** Mahasiswa dropout rata-rata hanya meluluskan 2,5 mata kuliah di semester 1 (graduate: 6,2). Mahasiswa dengan nilai semester 1 kosong (0) memiliki dropout rate 79%, dibanding 23% pada yang lain.
2. **Kondisi keuangan.** Mahasiswa dengan uang kuliah belum lunas dropout 87% (yang lunas 25%). Debitur 62% (non-debitur 28%). Penerima beasiswa hanya 12% (tanpa beasiswa 39%).
3. **Profil dan program studi.** Dropout naik tajam setelah usia 22 tahun dan mencapai sekitar 60% pada usia 26-30. Laki-laki dropout 45% (perempuan 25%). Program Equinculture, Informatics Engineering, dan Management kelas malam di atas 50%, sedangkan Nursing hanya 15%.

Indikator ekonomi makro (pengangguran, inflasi, GDP) hampir tidak berkorelasi dengan dropout, jadi bukan faktor yang perlu dikejar.

**Model prediksi.** Tiga model dibandingkan (Logistic Regression, Random Forest, Histogram Gradient Boosting). Logistic Regression dipilih karena sama baiknya dengan model kompleks, tidak overfitting, dan mudah dijelaskan. Pada data uji yang belum pernah dilihat, model mencapai **recall 0,80, precision 0,77, F1 0,79, dan ROC-AUC 0,91**. Artinya sekitar 8 dari 10 mahasiswa yang akan dropout terdeteksi setelah semester 1, dan 77% dari yang ditandai memang dropout.

Dengan demikian institusi kini dapat:
- **memahami** faktor penyebab dropout (analisis dan dashboard),
- **memantau** dropout rate secara rutin (dashboard Metabase), dan
- **mengenali lebih dini** mahasiswa berisiko (prototype Streamlit).



### Rekomendasi Action Items

- **Dampingi mahasiswa berisiko tinggi tepat setelah semester 1.** Jalankan prototype pada data semester 1 dan prioritaskan mahasiswa berstatus aktif dengan level risiko Tinggi (pada data ini 225 orang) untuk konseling akademik. Bila kapasitas konselor cukup, turunkan ambang risiko ke 0,3-0,4 agar lebih banyak mahasiswa dropout terjaring (recall naik dari 80% ke 89%), dengan konsekuensi lebih banyak alarm palsu.
- **Jadikan "nilai semester 1 kosong" dan "tidak lulus satu mata kuliah pun" sebagai pemicu intervensi.** Kedua sinyal ini mudah dipantau tiap semester lewat dashboard dan sudah berhubungan dengan dropout 79%.
- **Tangani masalah keuangan lebih awal.** Beri peringatan dan opsi cicilan atau keringanan bagi mahasiswa yang uang kuliahnya belum lunas atau berstatus debitur (dropout 87% dan 62%). Perluas beasiswa, karena penerimanya hanya 12% dropout.
- **Fokus pada program studi dengan dropout tinggi** (Equinculture, Informatics Engineering, Management kelas malam). Evaluasi beban kuliah, jadwal, dan dukungan belajar di program tersebut, dan pelajari praktik baik dari Nursing yang dropout-nya terendah.
- **Sediakan dukungan khusus untuk mahasiswa dewasa (usia > 22) dan kelas malam,** misalnya jadwal fleksibel, pembelajaran daring, dan mentor sebaya, karena dropout mereka jauh lebih tinggi.
- **Pantau dashboard secara berkala** (misalnya tiap awal dan akhir semester) dan catat hasil pendampingan.