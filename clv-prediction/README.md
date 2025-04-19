# Customer Lifetime Value (CLV) Prediction

This project is part of my learning journey to build business-relevant machine learning models. Here, I focused on predicting Customer Lifetime Value (CLV) based on firmographic, behavioral, and product-level features from a synthetic dataset.

The goal was to practice using real-world modeling techniques while thinking through what insights would be useful to Sales, Marketing, or Customer Success teams in a SaaS or B2B context.

---

## Why This Project

Customer Lifetime Value is typically measured after the fact (e.g., ACV × tenure). This project asks: **Can we learn what predicts high CLV early enough to influence it?**

I wanted to:
- Practice building a classification model using realistic features
- Understand what drives high-value customers
- Create business-friendly outputs like ranked segments and SHAP explainability

---

## What I'm Exploring

- What patterns are common among high-value customers?
- How might teams use this type of model in expansion or retention strategies?
- Can machine learning models help surface hidden opportunities in active accounts?

---

## Tools & Techniques Used

- Python, Pandas, scikit-learn, CatBoost
- Cross-validation with early stopping (to prevent overfitting)
- SHAP for explainable AI
- Visualization using matplotlib
- GitHub project structure and business documentation

---

## Modeling Summary

- Calculated a proxy for CLV as ACV × tenure
- Defined "high CLV" as the top 20% of customers
- Used a CatBoostClassifier to predict which customers are likely to fall into that high CLV group
- Applied Stratified K-Fold cross-validation and SHAP to validate results and interpret feature importance
- Segmented customers into deciles to simulate how teams might prioritize accounts

---

## What You’ll Find Here

- `clv_model.ipynb`: Full modeling workflow with markdown explanations
- `reports/`: Visual outputs for stakeholders
- `requirements/BRD.md`: A markdown version of the business requirements document
- A reproducible project folder designed for review, iteration, and growth

---

## What I'm Taking Away

- How to balance modeling performance with business relevance
- How to spot and avoid data leakage when features like tenure and revenue are involved
- How to structure a project for communication, not just computation

---

## Status

- This project is complete, but open to revision as I continue learning
- I welcome feedback from data professionals or business stakeholders
