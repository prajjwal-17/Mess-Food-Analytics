# Mess Food Waste Prediction System

A machine learning pipeline to predict monthly plate counts across university mess facilities — enabling smarter food preparation, reducing waste, and optimizing kitchen operations.

---

## Problem Statement

University mess kitchens over-prepare food because they have no reliable way to forecast how many students will show up for a given meal. This leads to:

- Significant food waste every month
- Excess spending on raw materials
- No data-driven basis for kitchen planning

This project tackles that by building a **Predictive Modeling engine** that forecasts monthly plate counts per mess, per meal — so kitchens prepare the right amount of food.

---

## Dataset

**File:** `final_training_data.csv`

| Column | Description |
|---|---|
| `Mess` | Name of the mess facility (6 messes) |
| `Month` | Month-Year of the record (e.g. `Apr-23`) |
| `Meal` | Meal type — `BF`, `LUNCH`, `SNACKS`, `DINNER` |
| `Waste_KG` | Food waste in kilograms that month |
| `Plates` | Total plates served that month **(prediction target)** |
| `Waste_Percent` | Waste as a percentage of food prepared |
| `Estimated_Dish` | `/`-separated list of dishes served |

- **12 months** of data: April 2023 → March 2024
- **6 mess facilities:** D-MESS, J-MESS, MEENAKSHI, SANNASI, SENBAGAM, STAFF MESS
- **288 rows** total (286 after removing closed-mess entries)

---

## Key Findings During Exploration

### 1. Dishes don't vary month to month
Every mess serves the **exact same menu** for a given meal across all 12 months. This means dish features cannot explain monthly plate variation on their own — they are constants per group.

### 2. Academic calendar drives plate count
Plate counts are strongly tied to the university semester cycle:

| Month | Phase | Avg Plates |
|---|---|---|
| Jun, Jan | Semester Break | ~10,000–27,000 |
| Jul | Transition | ~16,000 |
| May, Dec | End of Semester | ~21,000–33,000 |
| Aug–Nov, Feb–Apr | Full Semester | ~43,000–49,000 |

### 3. Mess size dominates predictions
SANNASI serves ~102,000 plates/month on average — roughly 4× that of D-MESS. The model must learn each mess's scale independently.

---

## Pipeline Versions

### `predictionEngine.ipynb` — Version 1

**Approach:** Feature-rich baseline using mess, meal, month, and multi-hot dish encoding.

**Features used:**
- `month_num`, `year`, `semester`, `is_holiday_month`
- One-hot encoding for `Meal` and `Mess`
- 31 binary dish columns (MultiLabelBinarizer)

**Models evaluated:** Random Forest, Gradient Boosting (5-Fold CV)

**Results:**

| Model | MAE | R² |
|---|---|---|
| Random Forest | ~13,267 plates | 0.117 |
| Gradient Boosting | ~12,640 plates | 0.230 |

**Why it underperformed:**
- Dish columns were all constants per Mess+Meal group — zero predictive signal
- `month_num` alone couldn't capture the semester break pattern
- No mess×meal interaction — SANNASI DINNER and MEENAKSHI DINNER treated similarly

---

### `predictiveEngineV2.ipynb` — Version 2

**What changed:**

1. **Dropped dish binary columns** — replaced with 4 derived menu score features using manually assigned popularity weights
2. **Added `academic_phase`** — encodes the semester calendar pattern directly (0=break, 1=transition, 2=end of semester, 3=full semester)
3. **Added cyclic month encoding** (`month_sin`, `month_cos`) — so December and January are treated as adjacent
4. **Added Mess×Meal interaction dummies** — each of the 24 Mess+Meal combinations gets its own baseline, capturing scale differences between facilities

**Features used:**

| Feature | Type | Purpose |
|---|---|---|
| `academic_phase` | Ordinal (0–3) | Semester calendar signal |
| `month_num` | Numeric | Raw month |
| `month_sin`, `month_cos` | Cyclic | Continuity across Dec→Jan |
| `menu_avg` | Float | Average dish popularity score |
| `menu_max` | Float | Star dish score (most popular item) |
| `menu_min` | Float | Weakest dish score |
| `menu_sum` | Float | Total menu weight |
| `mess_*` | One-hot | Mess identity |
| `meal_*` | One-hot | Meal type |
| `grp_{mess}_{meal}` | One-hot | Mess×Meal interaction **(key feature)** |

**Models evaluated:** Random Forest, Gradient Boosting, Ridge Regression (5-Fold CV)

**Results:**

| Model | MAE | MAPE | R² |
|---|---|---|---|
| Random Forest | ~4,246 plates | 32.4% | 0.971 |
| **Gradient Boosting**  | **~3,677 plates** | **33.7%** | **0.982** |
| Ridge Regression | ~12,664 plates | 91.6% | 0.743 |

**Improvement over V1:** MAE dropped from ~13,000 → ~3,677 (72% reduction). R² jumped from 0.23 → 0.98.

---

### `predictionEngineV3.ipynb` — Version 3 Current Best

**What changed from V2:**

The core insight here is that not all registered students actually show up — students skip meals for various reasons (early morning timings, being off-campus, eating outside). V3 incorporates **meal-weighted monthly skip counts** as a feature, and shifts the prediction target from gross plates to **net plates** (plates actually served after skips).

**Skip rate assumptions based on real student behaviour:**

| Meal | Skip Rate Range | Reason |
|---|---|---|
| BF | 18–30% | Earliest meal (6:30–9AM), classes start at 8AM |
| SNACKS | 12–22% | Optional meal, students often off-campus |
| DINNER | 8–16% | Some students eat outside |
| LUNCH | 3–9% | Peak meal, lowest skip rate |

Skip rates are further amplified during semester break months (Jun, Jan) and end-of-semester months (May, Dec) to reflect reduced campus presence.

**New feature vs V3:** `total_skips` — monthly count of meal opt-outs

**New target vs V3:** `net_plates` = `Plates - total_skips` (what the kitchen actually needs to serve)

**Results:**

| Model | MAE | MAPE | R² |
|---|---|---|---|
| Random Forest | ~4,542 plates | 29.9% | 0.957 |
| **Gradient Boosting** | **~4,202 plates** | **27.2%** | **0.967** |

**Improvement over V2:** MAPE dropped from 33.7% → 27.2%. Training error improved from 11.8% → 7.0%. The model now predicts what the kitchen actually needs to prepare, not just raw registrations.

> **Note:** Skip counts in V3 are currently simulated using the rates above. Once a real skip registration system is in place (e.g. students opting out the day before via a form), swap the simulated values with actual data — the pipeline stays identical.

---

## Dish Popularity Weights

Since menus are fixed per mess, raw dish presence adds no variation. Instead, each dish is assigned a **popularity score (0.0–1.0)** representing how much it drives student turnout. These are domain-knowledge priors.

| Dish | Score | | Dish | Score |
|---|---|---|---|---|
| Tea | 1.00 | | Pani Poori | 0.90 |
| Bread | 0.90 | | Steamed Rice | 0.90 |
| Poha | 0.90 | | Pongal | 0.85 |
| Biscuits | 0.80 | | Dal | 0.80 |
| Dal Tadka | 0.80 | | Idli | 0.80 |
| Palak Panneer | 0.80 | | Samosa | 0.80 |
| Vada | 0.80 | | Pav Baji | 0.80 |
| Rice | 0.77 | | Chicken | 0.70 |
| Chicken Curry | 0.70 | | Curd | 0.70 |
| Jeera Dal | 0.70 | | Kashmiri Dum Aloo | 0.70 |
| Paneer | 0.70 | | Poori | 0.70 |
| Sabzi | 0.70 | | Potato Masala | 0.67 |
| Roti | 0.67 | | Dosa | 0.60 |
| Upma | 0.60 | | Bonda | 0.60 |
| Chappathi | 0.50 | | Vegetable Curry | 0.50 |
| Panjabi Paratha | 0.50 | | Veg Kuruma | 0.30 |

These scores are collapsed into `menu_avg`, `menu_max`, `menu_min`, and `menu_sum` per row — giving the model a sense of how attractive each meal's menu is.

---

## Understanding the Metrics

| Metric | What it means |
|---|---|
| **MAE (Mean Absolute Error)** | On average, predictions are off by this many plates |
| **MAPE (Mean Absolute % Error)** | Average % error — more intuitive across different mess sizes |
| **R²** | How much variance the model explains (1.0 = perfect) |

> **Training error vs CV error:** Training error (~7% in V4) is optimistic — the model has already seen those rows. The honest real-world estimate is the **CV MAPE (~27% in V4)**, which will improve as more monthly data and real skip counts are added.

---

## Usage

**V2 — predict gross plate count:**
```python
# Predict plates for a given mess, meal, and month
predicted = predict_plates(
    mess      = 'D-MESS',
    meal      = 'LUNCH',
    month_str = 'Aug-24'
)
print(f"Predicted plates: {predicted:,}")
```

**V3 — predict net plates after skips:**
```python
# Provide expected monthly skip count for that mess+meal
predicted = predict_net_plates(
    mess           = 'D-MESS',
    meal           = 'LUNCH',
    month_str      = 'Aug-24',
    expected_skips = 800        # students who opted out this month
)
print(f"Net plates to prepare for: {predicted:,}")
```

---

## Repository Structure

```
├── predictionEngine.ipynb   # V1 — baseline pipeline
├── predictionEngineV2.nbipy         # V2 — dish weights + academic calendar
├── predictionEngineV3.ipynb        # V3 — skip-adjusted net plate prediction
└── README.md                      # This file
```

---

## Next Steps

- **Real skip data collection** — replace simulated skips with actual student opt-outs via a day-prior registration form; this is the single most impactful improvement for V4
- **Daily data collection** — monthly aggregation limits day-of-week signals; daily records would unlock much more granular predictions
- **Exam schedule integration** — exam periods suppress turnout; adding an `is_exam_week` flag would improve accuracy
- **Per-mess dish variation** — if menus start varying month to month, dish weights will become genuinely dynamic features
- **More months of data** — the single biggest lever to reduce the CV MAPE toward ~10%

---

## Dependencies

```
pandas
numpy
scikit-learn
```

Install with:
```bash
pip install pandas numpy scikit-learn
```