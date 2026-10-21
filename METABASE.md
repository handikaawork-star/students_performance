# Business Dashboard (Metabase)

Dashboard **Monitoring Dropout Mahasiswa - Jaya Jaya Institut** membantu institusi memantau dropout dan mengenali faktor penyebabnya.

## Akses

| | |
|---|---|
| URL | <http://localhost:3000> |
| Email | `root@mail.com` |
| Password | `root123` |

## Menjalankan

Prasyarat: Docker dan Docker Compose.

```bash
docker compose up -d
```

Perintah ini menjalankan:
- **Postgres** (`student-postgres`, port host 5434). Tabel `students` dibuat dari `sql/schema.sql` dan diisi dari `data/students_dashboard.csv` lewat `sql/load_data.sql`.
- **Metabase** (`student-metabase`, port 3000).

Tunggu sekitar 1 menit sampai Metabase siap, lalu buka <http://localhost:3000> dan login.

Koneksi database di Metabase: host `postgres`, port `5432`, database `student_db`, user `student_user`, password `student_password`.

### Dashboard sudah termuat otomatis

Tidak perlu setup manual. Berkas `metabase.db.mv.db` di root proyek adalah database internal Metabase yang sudah berisi akun, koneksi ke Postgres, dan dashboard. `docker-compose.yml` menyalinnya ke volume Metabase saat pertama kali dijalankan, jadi setelah `docker compose up -d` dan login, dashboard langsung tersedia.

Untuk mengulang dari kondisi awal (hapus semua data container, volume, dan perubahan di Metabase):

```bash
docker compose down -v
docker compose up -d
```

### Ekspor database Metabase

```bash
docker compose stop metabase
docker cp student-metabase:/metabase.db/metabase.db/metabase.db.mv.db ./
docker compose start metabase
```

Metabase dihentikan dulu supaya data tertulis penuh ke berkas.

## Isi dashboard

Semua kartu bisa difilter dengan **Program studi** dan **Jenis kelamin**.

| Kartu | Pertanyaan yang dijawab |
|---|---|
| Total mahasiswa, Dropout rate, Lulus, Aktif berisiko tinggi | Seberapa besar masalahnya? |
| Komposisi status | Berapa porsi Dropout, Graduate, dan Enrolled? |
| Dropout rate per kelompok usia | Siapa yang paling rentan? |
| Dropout rate menurut kondisi keuangan | Seberapa besar pengaruh uang kuliah, utang, dan beasiswa? |
| Dropout rate per program studi | Program mana yang perlu perhatian? |
| Rata-rata mata kuliah lulus per status | Bagaimana kinerja akademik tiap kelompok? |
| Sinyal dini: nilai semester 1 kosong | Apa tanda peringatan yang bisa dipantau? |
| Dropout rate menurut gender dan kelas | Adakah perbedaan antar profil? |
| Level risiko mahasiswa aktif | Siapa yang perlu didampingi sekarang? |

## Cara membaca

- **Dropout rate** dihitung terhadap seluruh mahasiswa, termasuk `Enrolled` yang statusnya belum final.
- **Level risiko** berasal dari model prediksi (Logistic Regression, data pendaftaran + semester 1). Skor >= 0,5 Tinggi, 0,3 sampai < 0,5 Sedang, selainnya Rendah. Untuk data ini skor dihitung pada data yang sama dengan data latih, sehingga dipakai untuk memprioritaskan pendampingan, bukan mengukur akurasi.
- Program studi dengan kurang dari 30 mahasiswa tidak ditampilkan karena angkanya tidak stabil.

## Temuan utama

- Dropout rate keseluruhan 32,1%.
- Uang kuliah belum lunas: 86,6% dropout (lunas: 24,7%). Debitur: 62,0%.
- Nilai semester 1 kosong: 79,4% dropout (ada nilai: 23,0%).
- Dropout naik tajam setelah usia 22 tahun, mencapai 59,8% pada usia 26-30 tahun.
- Dropout tertinggi: Equinculture (55%), Informatics Eng. (54%), Management malam (51%).
- 225 mahasiswa aktif berisiko tinggi dan layak didampingi lebih dulu.
