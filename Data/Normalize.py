import pandas as pd
import os


INPUT_FILE  = "mess_monthly_waste_analysis.csv"   # output from mess_analysis.py
OUTPUT_FILE = "cleaned_mess_data.csv"
COST_PER_KG = 40  # ₹ per kg of cooked food (ingredients + fuel)


if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(f"Could not find '{INPUT_FILE}'. Run mess_analysis.py first.")

df = pd.read_csv(INPUT_FILE)
print(f"Loaded {len(df)} rows from '{INPUT_FILE}'")
print(f"   Columns: {list(df.columns)}\n")


df['date'] = pd.to_datetime(df['MONTH'], format='%b-%Y')
df['month_num']  = df['date'].dt.month
df['year']       = df['date'].dt.year

# FLAG HOLIDAY MONTHS
# June = summer break, January = semester break

HOLIDAY_MONTHS = [1, 6]
df['is_holiday_month'] = df['month_num'].isin(HOLIDAY_MONTHS)

holiday_rows = df[df['is_holiday_month']]['MONTH'].unique()
print(f" Holiday months flagged: {list(holiday_rows)}")


# HANDLE SNACKS ZERO VALUES
# Snacks wastage IS real — food waste happens at snack time.
# These zeros mean the data was simply never entered/recorded by staff,
# NOT that there was no waste. Keeping 0 would be factually wrong.
# We replace with NaN = "data not recorded" so it's transparently
# excluded from averages rather than silently distorting them.

snacks_unrecorded = (df['SNACKS_WASTE'] == 0).sum()
df['snacks_data_recorded'] = df['SNACKS_WASTE'] != 0   # False = data gap, not zero waste

df['SNACKS_WASTE']   = df['SNACKS_WASTE'].replace(0, pd.NA)
df['SNACKS_PLATE']   = df['SNACKS_PLATE'].replace(0, pd.NA)
df['SNACKS_WASTE_%'] = df['SNACKS_WASTE_%'].replace(0, pd.NA)

print(f"⚠  Snacks: {snacks_unrecorded} rows had 0 → replaced with NaN (data not recorded, not zero waste).")


# TOTAL WASTE (grams → kg)
# Each wastage value is in grams (as recorded in the PDFs)

# Use fillna(0) only for summing — NaN snacks treated as 0 in total since data is missing
df['total_waste_grams'] = (
    df['BF_WASTE'].fillna(0) + df['LUNCH_WASTE'].fillna(0) +
    df['SNACKS_WASTE'].fillna(0) + df['DINNER_WASTE'].fillna(0)
)
df['total_waste_kg'] = df['total_waste_grams'].round(2)


# FINANCIAL LOSS ESTIMATE

df['financial_loss_inr'] = (df['total_waste_kg'] * COST_PER_KG).round(2)


# ACTIVE MEALS AVERAGE (skips NaN snacks months)
# skipna=True means months with missing snacks data are averaged
# across only BF, Lunch, Dinner for that row

active_meals = ['BF_WASTE_%', 'LUNCH_WASTE_%', 'SNACKS_WASTE_%', 'DINNER_WASTE_%']
df['active_meal_avg_waste_%'] = df[active_meals].mean(axis=1, skipna=True).apply(round)


# ANOMALY FLAG
# Flag months where waste % is unusually high (> 2x the global mean)
# Excludes holiday months from baseline calculation

baseline_mean = df[~df['is_holiday_month']]['active_meal_avg_waste_%'].mean()
baseline_std  = df[~df['is_holiday_month']]['active_meal_avg_waste_%'].std()
threshold     = round(baseline_mean + 2 * baseline_std, 2)

df['is_anomaly'] = (~df['is_holiday_month']) & (df['active_meal_avg_waste_%'] > threshold)

anomalies = df[df['is_anomaly']][['MESS_NAME', 'MONTH', 'active_meal_avg_waste_%']]
print(f"\nBaseline avg waste (non-holiday): {baseline_mean:.1f}%  |  Anomaly threshold: {threshold}%")
if not anomalies.empty:
    print(f"Anomalies detected:\n{anomalies.to_string(index=False)}")
else:
    print("no anomalies detected.")


output_cols = [
    # Identity
    "MESS_NAME", "MONTH", "date", "month_num", "year",
    # Flags
    "is_holiday_month", "snacks_data_recorded", "is_anomaly",
    # Raw waste
    "BF_WASTE", "LUNCH_WASTE", "SNACKS_WASTE", "DINNER_WASTE", "total_waste_grams", "total_waste_kg",
    # Plate counts
    "BF_PLATE", "LUNCH_PLATE", "SNACKS_PLATE", "DINNER_PLATE",
    # Waste percentages
    "BF_WASTE_%", "LUNCH_WASTE_%", "SNACKS_WASTE_%", "DINNER_WASTE_%",
    "MONTH_AVG_WASTE_%", "active_meal_avg_waste_%",
    # Financial
    "financial_loss_inr",
]

df_out = df[output_cols]
df_out.to_csv(OUTPUT_FILE, index=False)


print(f"\n{'='*55}")
print(f"Normalization Complete → '{OUTPUT_FILE}'")
print(f"{'='*55}")
print(f"  Total rows        : {len(df_out)}")
print(f"  Messes            : {df_out['MESS_NAME'].nunique()} ({', '.join(df_out['MESS_NAME'].unique())})")
print(f"  Date range        : {df_out['date'].min().strftime('%b %Y')} → {df_out['date'].max().strftime('%b %Y')}")
print(f"  Holiday rows      : {df_out['is_holiday_month'].sum()}")
print(f"  Anomaly rows      : {df_out['is_anomaly'].sum()}")
print(f"  Total waste (kg)  : {df_out['total_waste_kg'].sum():,.1f} kg")
print(f"  Total fin. loss   : ₹{df_out['financial_loss_inr'].sum():,.2f}")
print(f"  Cost assumption   : ₹{COST_PER_KG}/kg")