"""Prediksi risiko dropout mahasiswa dari file CSV.

Contoh:
    python main.py
    python main.py --input data/mahasiswa_baru.csv --output data/hasil.csv --top 20
    python main.py --active-only
"""
import argparse
import sys

import joblib
import pandas as pd

MODEL_PATH = "model/dropout_model.joblib"
HIGH, MEDIUM = 0.5, 0.3


def risk_level(score):
    return "Tinggi" if score >= HIGH else "Sedang" if score >= MEDIUM else "Rendah"


def add_derived_features(df):
    """Fitur turunan yang dibuat di notebook: tingkat kelulusan semester 1."""
    if "approval_rate_1st_sem" not in df.columns:
        enrolled = df["Curricular_units_1st_sem_enrolled"].replace(0, float("nan"))
        df = df.assign(
            approval_rate_1st_sem=(df["Curricular_units_1st_sem_approved"] / enrolled).fillna(0)
        )
    return df


def predict(df, model, ids):
    cols = list(model.named_steps["preprocess"].feature_names_in_)
    df = add_derived_features(df)
    missing = [c for c in cols if c not in df.columns]
    if missing:
        sys.exit(f"Kolom berikut tidak ada di input: {missing}")
    return pd.DataFrame({
        "student_id": ids,
        "risk_score": model.predict_proba(df[cols])[:, 1].round(4),
        "predicted_dropout": model.predict(df[cols]),
    })


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default="data/students_performance.csv", help="CSV data mahasiswa")
    ap.add_argument("--sep", default=";", help="pemisah kolom CSV input")
    ap.add_argument("--output", default="data/students_risk.csv", help="CSV hasil prediksi")
    ap.add_argument("--model", default=MODEL_PATH, help="path model joblib")
    ap.add_argument("--id-col", default=None, help="kolom ID mahasiswa (default: nomor baris mulai dari 1)")
    ap.add_argument("--top", type=int, default=10, help="jumlah mahasiswa berisiko tertinggi yang ditampilkan")
    ap.add_argument("--active-only", action="store_true",
                    help="hanya prediksi mahasiswa yang masih aktif (Status Enrolled atau kosong)")
    args = ap.parse_args()

    df = pd.read_csv(args.input, sep=args.sep)
    if args.id_col and args.id_col not in df.columns:
        sys.exit(f"Kolom {args.id_col} tidak ada di input.")
    if args.active_only:
        if "Status" not in df.columns:
            sys.exit("--active-only butuh kolom Status di input.")
        df = df[df["Status"].isna() | (df["Status"] == "Enrolled")]

    ids = df[args.id_col].to_numpy() if args.id_col else df.index.to_numpy() + 1
    result = predict(df, joblib.load(args.model), ids)
    result.to_csv(args.output, index=False)

    level = result["risk_score"].map(risk_level)
    print(f"{len(result)} mahasiswa diprediksi -> {args.output}")
    print(f"Diprediksi dropout: {int(result['predicted_dropout'].sum())} ({result['predicted_dropout'].mean():.1%})")
    print("Level risiko:", level.value_counts().reindex(["Tinggi", "Sedang", "Rendah"], fill_value=0).to_dict())
    top = result.assign(risk_level=level).nlargest(args.top, "risk_score")
    print(f"\n{args.top} mahasiswa berisiko tertinggi:")
    print(top.to_string(index=False))
    print("\nCatatan: skor dipakai untuk mengurutkan prioritas pendampingan, bukan probabilitas sebenarnya.")


if __name__ == "__main__":
    main()
