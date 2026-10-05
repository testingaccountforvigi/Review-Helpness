# Dataset: Helpful Sentences from Reviews

**Official source:** Amazon Open Data Registry
https://registry.opendata.aws/helpful-sentences-from-reviews/

**Paper:** Gamzu et al., *Identifying Helpful Sentences in Product Reviews*, NAACL 2021
https://aclanthology.org/2021.naacl-main.55/

## Why this dataset is a strong fit
- Directly measures review-sentence helpfulness instead of using an indirect proxy.
- Exactly 20,000 annotated training sentences and 2,000 test sentences.
- Human labels are on a 0–2 helpfulness scale.
- Data covers 123 products across Toys, Books, Movies, Music, Camera and Electronics.
- The source is publicly listed by Amazon and distributed from an open S3 bucket.

## Model target
`helpful` is the continuous target. The app reports a predicted score from 0 to 2. For a simple interpretation, scores >= 1.5 are considered **Highly Helpful**, scores 1.0–1.49 **Helpful**, and scores below 1.0 **Needs More Detail**.

## Leakage control
Product ASIN and the original helpful label are never used as model features. The model uses only the review sentence text, keeping the relationship with written-review characteristics direct and simple.
