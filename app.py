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

st.set_page_config(page_title="Prediksi Dropout - Jaya Jaya Institut", page_icon="🎓", layout="wide")


@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    with open(MEANS_PATH) as f:
        means = np.array(json.load(f))
    return model, means


@st.cache_data
def load_defaults():
    """Nilai tipikal (median) tiap fitur, dipakai untuk kolom yang tidak ditanyakan di form."""
    df = pd.read_csv(DATA_PATH, sep=";")
    return df.median(numeric_only=True).to_dict()


def add_derived_features(df):
    enrolled = df["Curricular_units_1st_sem_enrolled"].replace(0, np.nan)
    return df.assign(approval_rate_1st_sem=(df["Curricular_units_1st_sem_approved"] / enrolled).fillna(0))


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
defaults = load_defaults()
cols = list(model.named_steps["preprocess"].feature_names_in_)

st.title("🎓 Prediksi Risiko Dropout Mahasiswa")
st.caption(
    "Prototype untuk Jaya Jaya Institut. Model: Logistic Regression yang dilatih pada mahasiswa berstatus "
    "Dropout (1) dan Graduate (0), memakai data pendaftaran dan semester 1, sehingga dapat dipakai begitu "
    "semester 1 selesai. Mahasiswa Enrolled tidak dipakai untuk melatih model, melainkan menjadi sasaran prediksi."
)

tab_single, tab_batch = st.tabs(["Satu mahasiswa", "Banyak mahasiswa (CSV)"])

with tab_single:
    with st.form("form"):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.subheader("Profil")
            course = st.selectbox("Program studi", list(COURSES), index=list(COURSES).index(9500),
                                  format_func=COURSES.get)
            age = st.number_input("Usia saat mendaftar", 17, 70, 20)
            gender = st.radio("Jenis kelamin", [0, 1], format_func=lambda x: "Laki-laki" if x else "Perempuan",
                              horizontal=True)
            evening = st.radio("Kelas", [1, 0], format_func=lambda x: "Siang" if x else "Malam", horizontal=True)
            displaced = st.checkbox("Perantau (pindah dari daerah asal)")
            admission = st.number_input("Nilai masuk (0-200)", 0.0, 200.0, float(defaults["Admission_grade"]))
        with c2:
            st.subheader("Keuangan")
            fees = st.checkbox("Uang kuliah lunas tepat waktu", value=True)
            debtor = st.checkbox("Tercatat sebagai debitur")
            scholarship = st.checkbox("Penerima beasiswa")
        with c3:
            st.subheader("Semester 1")
            enrolled = st.number_input("Mata kuliah diambil", 0, 30, 6)
            approved = st.number_input("Mata kuliah lulus", 0, 30, 5)
            grade = st.number_input("Rata-rata nilai (0-20, isi 0 jika belum ada)", 0.0, 20.0, 12.0)
            evals = st.number_input("Jumlah evaluasi/ujian", 0, 50, 8)
        submitted = st.form_submit_button("Prediksi", type="primary")

    if submitted:
        if approved > enrolled:
            st.error("Mata kuliah lulus tidak boleh lebih besar dari mata kuliah diambil.")
        else:
            row = {c: defaults.get(c, 0) for c in cols}
            row.update({
                "Course": course, "Age_at_enrollment": age, "Gender": gender,
                "Daytime_evening_attendance": evening, "Displaced": int(displaced),
                "Admission_grade": admission, "Tuition_fees_up_to_date": int(fees),
                "Debtor": int(debtor), "Scholarship_holder": int(scholarship),
                "Curricular_units_1st_sem_enrolled": enrolled,
                "Curricular_units_1st_sem_approved": approved,
                "Curricular_units_1st_sem_grade": grade,
                "Curricular_units_1st_sem_evaluations": evals,
            })
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
            st.caption("Kolom yang tidak ada di form diisi nilai median data latih.")

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
