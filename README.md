# ReviewRadar — Review Helpfulness Analysis

## Dataset
**Helpful Sentences from Reviews** — Amazon Open Data Registry.

The dataset contains **20,000 training sentences and 2,000 test sentences**, with human helpfulness scores from **0 to 2**. The benchmark was created from 45,091 Amazon reviews across 123 products and six categories; each training sentence was rated by 10 annotators and each test sentence by 30 annotators.

Source: https://registry.opendata.aws/helpful-sentences-from-reviews/
Paper: https://aclanthology.org/2021.naacl-main.55/

## Project
The model estimates sentence helpfulness for a purchase decision from the review sentence itself. The core model is **TF-IDF + Ridge Regression**, a simple, explainable model that is also used in the original benchmark paper.

The project reports standard regression metrics (MAE, MSE, R², Pearson correlation) plus an easy-to-understand **±0.5 score accuracy**: the percentage of test predictions whose error is at most 0.5 helpfulness points.

## Files
- `review_helpfulness.ipynb` — concise end-to-end notebook with EDA, preprocessing, training and evaluation.
- `model_utils.py` — shared data/model code.
- `app.py` — interactive Streamlit application.
- `Machine_Learning_Case_Study_Documentation.docx` — final report structure with screenshot spaces.

## Run notebook
```bash
pip install -r requirements.txt
jupyter notebook review_helpfulness.ipynb
```

The notebook downloads the official public `train.json` and `test.json` files automatically.

## Run Streamlit
```bash
streamlit run app.py
```

The first app run downloads the public dataset and trains the model; the trained artifact is then cached in `artifacts/`.

## Important
The notebook and app never hard-code an accuracy value. All performance numbers come from the official held-out test set after the model is actually trained.
