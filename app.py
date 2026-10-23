"""Prototype Streamlit: prediksi risiko dropout mahasiswa Jaya Jaya Institut.

Jalankan: streamlit run app.py
"""
import json

import joblib
import numpy as np
import pandas as pd
import streamlit as st

MODEL_PATH = "model/dropout_model.joblib"
MEANS_PATH = "model/feature_means.json"
DATA_PATH = "data/students_performance.csv"
HIGH, MEDIUM = 0.5, 0.3

COURSES = {
    33: "Biofuel Production", 171: "Animation & Multimedia", 8014: "Social Service (malam)",
    9003: "Agronomy", 9070: "Communication Design", 9085: "Veterinary Nursing",
    9119: "Informatics Eng.", 9130: "Equinculture", 9147: "Management",
    9238: "Social Service", 9254: "Tourism", 9500: "Nursing", 9556: "Oral Hygiene",
    9670: "Advertising & Marketing", 9773: "Journalism", 9853: "Basic Education",
    9991: "Management (malam)",
}

MARITAL = {1: "Lajang", 2: "Menikah", 3: "Duda/Janda (pasangan meninggal)", 4: "Bercerai",
           5: "Kumpul kebo (facto union)", 6: "Berpisah secara hukum"}

st.set_page_config(page_title="Prediksi Dropout - Jaya Jaya Institut", page_icon="🎓", layout="wide")


@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    with open(MEANS_PATH) as f:
        means = np.array(json.load(f))
    return model, means


@st.cache_data
def load_reference():
    """Data acuan hanya untuk pilihan dan nilai awal isian form; tidak dipakai untuk mengisi fitur secara diam-diam."""
    return pd.read_csv(DATA_PATH, sep=";")


def add_derived_features(df):
    enrolled = df["Curricular_units_1st_sem_enrolled"].replace(0, np.nan)
    return df.assign(approval_rate_1st_sem=(df["Curricular_units_1st_sem_approved"] / enrolled).fillna(0))


def code_select(label, col, help_text="Kode sesuai data/README.md"):
    """Pilihan kode kategori yang ada di dataset; kosong sampai pengguna memilih."""
    return st.selectbox(label, sorted(ref[col].unique().tolist()), index=None, placeholder="Pilih", help=help_text)


def number(label, col, **kw):
    """Isian angka dengan rentang dari dataset; kosong sampai pengguna mengisi."""
    lo, hi = ref[col].min(), ref[col].max()
    cast = int if pd.api.types.is_integer_dtype(ref[col]) else float
    return st.number_input(label, cast(lo), cast(hi), value=None, placeholder="Isi", **kw)


def risk_level(score):
    return "Tinggi" if score >= HIGH else "Sedang" if score >= MEDIUM else "Rendah"


def explain(model, means, row):
    """Kontribusi tiap fitur asli terhadap log-odds risiko, dibanding rata-rata mahasiswa data latih."""
    prep, clf = model.named_steps["preprocess"], model.named_steps["model"]
    names = prep.get_feature_names_out()
    contrib = clf.coef_[0] * (prep.transform(row)[0] - means)
    nominal = list(prep.named_transformers_["nominal"].feature_names_in_)
    original = []
    for n in names:
        col = n.split("__", 1)[1]
        original.append(next((f for f in nominal if col.startswith(f + "_")), col))
    return pd.Series(contrib, index=original).groupby(level=0).sum().sort_values()


model, means = load_model()
ref = load_reference()
cols = list(model.named_steps["preprocess"].feature_names_in_)

st.title("🎓 Prediksi Risiko Dropout Mahasiswa")
st.caption(
    "Prototype untuk Jaya Jaya Institut. Model: Logistic Regression yang dilatih pada mahasiswa berstatus "
    "Dropout (1) dan Graduate (0), memakai data pendaftaran dan semester 1, sehingga dapat dipakai begitu "
    "semester 1 selesai. Mahasiswa Enrolled tidak dipakai untuk melatih model, melainkan menjadi sasaran prediksi."
)

tab_single, tab_batch = st.tabs(["Satu mahasiswa", "Banyak mahasiswa (CSV)"])

with tab_single:
    st.caption("Isi semua kolom dengan data aktual mahasiswa. Seluruh fitur yang dipakai model berasal dari form ini, "
               "tanpa nilai pengganti otomatis.")
    with st.form("form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Profil")
            course = st.selectbox("Program studi", list(COURSES), index=None, placeholder="Pilih",
                                  format_func=COURSES.get)
            age = st.number_input("Usia saat mendaftar", 17, 70, value=None, placeholder="Isi")
            gender = st.radio("Jenis kelamin", [0, 1], index=None,
                              format_func=lambda x: "Laki-laki" if x else "Perempuan", horizontal=True)
            marital = st.selectbox("Status pernikahan", list(MARITAL), index=None, placeholder="Pilih",
                                   format_func=MARITAL.get)
            nationality = code_select("Kewarganegaraan (kode)", "Nacionality")
            international = st.checkbox("Mahasiswa internasional")
            special_needs = st.checkbox("Berkebutuhan pendidikan khusus")
            displaced = st.checkbox("Perantau (pindah dari daerah asal)")
            evening = st.radio("Kelas", [1, 0], index=None,
                               format_func=lambda x: "Siang" if x else "Malam", horizontal=True)
        with c2:
            st.subheader("Pendaftaran dan keluarga")
            app_mode = code_select("Jalur pendaftaran (kode)", "Application_mode")
            app_order = number("Urutan pilihan pendaftaran (0-9)", "Application_order")
            prev_qual = code_select("Kualifikasi sebelumnya (kode)", "Previous_qualification")
            prev_grade = number("Nilai kualifikasi sebelumnya (0-200)", "Previous_qualification_grade")
            admission = number("Nilai masuk (0-200)", "Admission_grade")
            mother_qual = code_select("Pendidikan ibu (kode)", "Mothers_qualification")
            father_qual = code_select("Pendidikan ayah (kode)", "Fathers_qualification")
            mother_occ = code_select("Pekerjaan ibu (kode)", "Mothers_occupation")
            father_occ = code_select("Pekerjaan ayah (kode)", "Fathers_occupation")
        with c3:
            st.subheader("Keuangan dan semester 1")
            fees = st.checkbox("Uang kuliah lunas tepat waktu")
            debtor = st.checkbox("Tercatat sebagai debitur")
            scholarship = st.checkbox("Penerima beasiswa")
            credited = number("Mata kuliah diakui (credited)", "Curricular_units_1st_sem_credited")
            enrolled = number("Mata kuliah diambil", "Curricular_units_1st_sem_enrolled")
            approved = number("Mata kuliah lulus", "Curricular_units_1st_sem_approved")
            grade = number("Rata-rata nilai (0-20, isi 0 jika belum ada)", "Curricular_units_1st_sem_grade")
            evals = number("Jumlah evaluasi/ujian", "Curricular_units_1st_sem_evaluations")
            no_evals = number("Mata kuliah tanpa evaluasi", "Curricular_units_1st_sem_without_evaluations")
        st.subheader("Kondisi makro saat mendaftar")
        m1c, m2c, m3c = st.columns(3)
        with m1c:
            unemployment = number("Tingkat pengangguran (%)", "Unemployment_rate")
        with m2c:
            inflation = number("Tingkat inflasi (%)", "Inflation_rate")
        with m3c:
            gdp = number("GDP (pertumbuhan, %)", "GDP")
        submitted = st.form_submit_button("Prediksi", type="primary")

    if submitted:
        row = {
            "Marital_status": marital, "Application_mode": app_mode, "Application_order": app_order,
            "Course": course, "Daytime_evening_attendance": evening,
            "Previous_qualification": prev_qual, "Previous_qualification_grade": prev_grade,
            "Nacionality": nationality, "Mothers_qualification": mother_qual,
            "Fathers_qualification": father_qual, "Mothers_occupation": mother_occ,
            "Fathers_occupation": father_occ, "Admission_grade": admission,
            "Displaced": int(displaced), "Educational_special_needs": int(special_needs),
            "Debtor": int(debtor), "Tuition_fees_up_to_date": int(fees), "Gender": gender,
            "Scholarship_holder": int(scholarship), "Age_at_enrollment": age,
            "International": int(international),
            "Curricular_units_1st_sem_credited": credited,
            "Curricular_units_1st_sem_enrolled": enrolled,
            "Curricular_units_1st_sem_evaluations": evals,
            "Curricular_units_1st_sem_approved": approved,
            "Curricular_units_1st_sem_grade": grade,
            "Curricular_units_1st_sem_without_evaluations": no_evals,
            "Unemployment_rate": unemployment, "Inflation_rate": inflation, "GDP": gdp,
        }
        empty = [k for k, v in row.items() if v is None]
        if empty:
            st.error(f"Lengkapi semua kolom sebelum memprediksi. Belum diisi: {', '.join(empty)}")
        elif approved > enrolled:
            st.error("Mata kuliah lulus tidak boleh lebih besar dari mata kuliah diambil.")
        else:
            X = add_derived_features(pd.DataFrame([row]))[cols]
            score = float(model.predict_proba(X)[0, 1])
            level = risk_level(score)

            m1, m2 = st.columns(2)
            m1.metric("Skor risiko dropout", f"{score:.0%}")
            m2.metric("Level risiko", level)
            msg = {"Tinggi": st.error, "Sedang": st.warning, "Rendah": st.success}[level]
            msg({
                "Tinggi": "Prioritaskan pendampingan akademik dan keuangan.",
                "Sedang": "Pantau perkembangan dan tawarkan konseling.",
                "Rendah": "Risiko rendah, tidak perlu tindakan khusus.",
            }[level])

            st.subheader("Faktor yang memengaruhi skor")
            st.caption("Dibanding mahasiswa rata-rata. Merah menaikkan risiko, hijau menurunkannya.")
            contrib = explain(model, means, X)
            top = pd.concat([contrib.head(5), contrib.tail(5)]).drop_duplicates()
            top = top[top.abs() > 0.01]
            st.bar_chart(pd.DataFrame({"pengaruh": top}).assign(
                color=np.where(top > 0, "#e76f51", "#2a9d8f")), y="pengaruh", color="color", horizontal=True)

with tab_batch:
    st.write(
        "Unggah CSV data mahasiswa (pemisah `;`, kolom sama seperti `data/students_performance.csv`). "
        "Kolom semester 2 dan `Status` boleh ada, akan diabaikan oleh model."
    )
    up = st.file_uploader("File CSV", type="csv")
    if st.button("Atau coba dengan mahasiswa Enrolled dari dataset"):
        st.session_state["use_enrolled"] = True
    if up:
        st.session_state["use_enrolled"] = False
    if up or st.session_state.get("use_enrolled"):
        if up:
            data = pd.read_csv(up, sep=";")
        else:
            data = pd.read_csv(DATA_PATH, sep=";").query("Status == 'Enrolled'").reset_index(drop=True)
            st.caption(f"Menampilkan prediksi untuk {len(data)} mahasiswa berstatus Enrolled.")
        data = add_derived_features(data)
        missing = [c for c in cols if c not in data.columns]
        if missing:
            st.error(f"Kolom berikut tidak ada di file: {missing}")
        else:
            res = data.assign(
                risk_score=model.predict_proba(data[cols])[:, 1].round(4),
            )
            res["risk_level"] = res["risk_score"].map(risk_level)
            counts = res["risk_level"].value_counts().reindex(["Tinggi", "Sedang", "Rendah"], fill_value=0)
            a, b, c = st.columns(3)
            a.metric("Risiko tinggi", int(counts["Tinggi"]))
            b.metric("Risiko sedang", int(counts["Sedang"]))
            c.metric("Risiko rendah", int(counts["Rendah"]))
            show = res.sort_values("risk_score", ascending=False)
            st.dataframe(show[["risk_score", "risk_level"] + cols], use_container_width=True)
            st.download_button("Unduh hasil (CSV)", show.to_csv(index=False).encode(),
                               "hasil_prediksi.csv", "text/csv")

st.divider()
st.caption(
    "Skor dipakai untuk mengurutkan prioritas pendampingan, bukan probabilitas sebenarnya. "
    "Skor tinggi berarti pola mahasiswa mirip mahasiswa yang dropout, bukan kepastian akan dropout."
)
