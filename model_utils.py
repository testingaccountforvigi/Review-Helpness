# The joblib file is not executed directly. It is loaded by Python using joblib.load() when the prediction function needs the trained model. This allows the application to reuse the trained model without retraining it.

from pathlib import Path
import json
import requests
import joblib
import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

TRAIN_URL = "https://helpful-sentences-from-reviews.s3.amazonaws.com/train.json"
TEST_URL = "https://helpful-sentences-from-reviews.s3.amazonaws.com/test.json"
ARTIFACT_DIR = Path(__file__).resolve().parent / "artifacts"
MODEL_FILE = ARTIFACT_DIR / "review_helpfulness_ridge.joblib"
METRICS_FILE = ARTIFACT_DIR / "metrics.json"


def read_json_lines(url):
    response = requests.get(url, timeout=60)
    response.raise_for_status()
    return pd.DataFrame(
        [json.loads(line) for line in response.text.splitlines() if line.strip()]
    )


def load_data():
    return read_json_lines(TRAIN_URL), read_json_lines(TEST_URL)


def clean_data(df):
    """Keep the cleaning minimal so the official 20k/2k split stays intact."""
    df = df[["asin", "sentence", "helpful", "product_title"]].copy()
    df["sentence"] = df["sentence"].fillna("").astype(str)
    df["product_title"] = df["product_title"].fillna("").astype(str)
    df["sentence"] = df["sentence"].str.replace(r"<[^>]+>", " ", regex=True)
    df["sentence"] = df["sentence"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["product_title"] = df["product_title"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["helpful"] = pd.to_numeric(df["helpful"], errors="coerce")
    df = df.dropna(subset=["helpful"])
    df = df[df["sentence"].str.len() > 0]
    df = df.drop_duplicates(subset=["asin", "sentence"])
    df["model_text"] = df["sentence"]
    df["length"] = df["sentence"].str.len()
    return df.reset_index(drop=True)


def calculate_metrics(true, pred):
    mae = mean_absolute_error(true, pred)
    mse = mean_squared_error(true, pred)
    r2 = r2_score(true, pred)
    pearson = pearsonr(true, pred).statistic
    within_half = float(np.mean(np.abs(true - pred) <= 0.5) * 100)
    return {
        "mae": float(mae),
        "mse": float(mse),
        "r2": float(r2),
        "pearson": float(pearson),
        "within_half_accuracy": within_half,
    }


def train_model(train_df, test_df):
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2), min_df=2, max_features=15000, sublinear_tf=True
    )
    X_train = vectorizer.fit_transform(train_df["model_text"])
    X_test = vectorizer.transform(test_df["model_text"])

    # Honest baseline: always predict the training-set average.
    baseline_pred = np.repeat(train_df["helpful"].mean(), len(test_df))
    baseline_metrics = calculate_metrics(test_df["helpful"].to_numpy(), baseline_pred)

    # Final model: regularized linear regression is a strong fit for TF-IDF text features.
    model = Ridge(alpha=2.0)
    model.fit(X_train, train_df["helpful"])
    pred = np.clip(model.predict(X_test), 0, 2)
    true = test_df["helpful"].to_numpy()
    model_metrics = calculate_metrics(true, pred)

    metrics = {
        **model_metrics,
        "baseline_mae": baseline_metrics["mae"],
        "baseline_mse": baseline_metrics["mse"],
        "baseline_r2": baseline_metrics["r2"],
        "baseline_pearson": baseline_metrics["pearson"],
        "baseline_within_half_accuracy": baseline_metrics["within_half_accuracy"],
        "train_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "features": int(X_train.shape[1]),
    }

    ARTIFACT_DIR.mkdir(exist_ok=True)
    joblib.dump({"vectorizer": vectorizer, "model": model}, MODEL_FILE)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2))
    return model, vectorizer, metrics, pred


def ensure_model():
    if MODEL_FILE.exists() and METRICS_FILE.exists():
        artifact = joblib.load(MODEL_FILE)
        metrics = json.loads(METRICS_FILE.read_text())
        return artifact["model"], artifact["vectorizer"], metrics

    train_raw, test_raw = load_data()
    train_df = clean_data(train_raw)
    test_df = clean_data(test_raw)
    model, vectorizer, metrics, _ = train_model(train_df, test_df)
    return model, vectorizer, metrics


def predict(sentence, product_title=""):
    model, vectorizer, metrics = ensure_model()
    text = sentence.strip()
    X = vectorizer.transform([text])
    score = float(np.clip(model.predict(X)[0], 0, 2))

    if score >= 1.5:
        band = "Highly Helpful"
    elif score >= 1.0:
        band = "Helpful"
    else:
        band = "Needs More Detail"
    return score, band, metrics
