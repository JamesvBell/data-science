# Business Requirements Document  
**Project Title:** CLV Prediction Across Active & Churned Customers  
**Folder:** `data-science/clv-prediction/requirements/`  
**Version:** v3 – Final Model Scope  

---

## 1. Objective

Develop a machine learning model to estimate **Customer Lifetime Value (CLV)** across both **active and churned customers** using firmographic, behavioral, and product-based features.

The goal is to help Sales, Marketing, and Customer Success identify:
- High-potential customers for **upsell or retention**
- Common traits among **high-value profiles**
- Strategic segments for **account targeting and expansion**

---

## 2. Business Questions

- Which firmographic or usage behaviors are most predictive of high CLV?
- Can we identify actionable profiles of high-value customers?
- How does predicted CLV vary by region, product tier, and customer engagement?
- What segments show opportunity to expand, prevent churn, or prioritize investment?

---

## 3. Stakeholders

| Stakeholder        | Role                             |
|--------------------|----------------------------------|
| Customer Success   | Target proactive outreach        |
| Sales              | Focus expansion and new logo efforts |
| Marketing          | Improve campaign targeting       |
| FP&A               | Inform planning and revenue modeling |

---

## 4. Data Sources

- Synthetic customer master (region, industry, geo, company size)
- Behavioral metrics (monthly logins, support tickets, feature usage)
- Financial metrics (ACV, tenure)
- Customer status and engagement (email scores, churned flag)

---

## 5. Modeling Approach

- Calculate proxy CLV = ACV × Tenure (months ÷ 12)
- Define `high_clv_flag` as top 20% of CLV values
- Train a **CatBoostClassifier** on all customers to predict `high_clv_flag`
- Use **Stratified K-Fold Cross-Validation** with **early stopping** to avoid overfitting
- Apply **SHAP** to understand global and local drivers
- Segment output into **deciles** (1 = lowest, 10 = highest predicted CLV)

---

## 6. Deliverables

- Trained classification model predicting high-CLV likelihood
- Customer scoring dataset with:
  - `predicted_clv_prob`
  - `clv_segment` (1–10)
- SHAP-based driver analysis (feature importance, dependence)
- Charts:
  - Industry composition by CLV segment
  - Avg feature usage score by segment
- `notebooks/` and `reports/` folder with reproducible, interpretable outputs

---

## 7. Success Criteria

- **ROC AUC ≥ 0.90** with reasonable precision/recall for high-CLV detection
- Clear, validated drivers (e.g. product tier, usage, engagement)
- Prioritization lists for GTM teams
- Notebook published to GitHub with markdown commentary and charts
- No data leakage; model structure reviewed for production suitability

---

## 8. Notes & Assumptions

- Engagement features like `support_tickets` and `email_engagement` are assumed to be available within the **early customer lifecycle**
- This is a **static scoring model**, not time-aware or decay-based
- All data is synthetic; structure reflects real business-like use cases
