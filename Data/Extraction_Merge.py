import pdfplumber
import pandas as pd
import os
import re


ROOT_FOLDER = r"D:\Foundathon3.0\Foundation\Foundation"


def extract_mess_name_from_pdf(path):
    """Pull mess name from the 2nd header row inside the PDF itself."""
    with pdfplumber.open(path) as pdf:
        tables = pdf.pages[0].extract_tables()
        if tables and len(tables[0]) >= 2:
            header_cell = tables[0][1][0]  # e.g. "MESS WISE REPORT-D- MESS"
            if header_cell:
                # Take everything after the last dash
                parts = header_cell.split("-")
                return parts[-1].strip().upper()
    return None


def parse_food_pdf(path):
    """
    Extract monthly food wastage from PDF.
    Columns in PDF: S.NO | MONTH | BF | LUNCH | SNACKS | DINNER | TOTAL
    Indices:          0      1      2     3        4        5       6
    """
    with pdfplumber.open(path) as pdf:
        rows = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Keep only data rows: col[0] is a digit (S.NO)
                    if row[0] and str(row[0]).strip().isdigit():
                        rows.append({
                            "MONTH":        str(row[1]).strip(),
                            "BF_WASTE":     pd.to_numeric(row[2], errors="coerce"),
                            "LUNCH_WASTE":  pd.to_numeric(row[3], errors="coerce"),
                            "SNACKS_WASTE": pd.to_numeric(row[4], errors="coerce"),
                            "DINNER_WASTE": pd.to_numeric(row[5], errors="coerce"),
                        })
    return pd.DataFrame(rows)


def parse_plate_pdf(path):
    """
    Extract monthly plate counts from PDF.
    Columns in PDF: S.NO | MONTH | BF | LUNCH | SNACKS | DINNER | TOTAL
    Indices:          0      1      2     3        4        5       6
    """
    with pdfplumber.open(path) as pdf:
        rows = []
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    if row[0] and str(row[0]).strip().isdigit():
                        rows.append({
                            "MONTH":         str(row[1]).strip(),
                            "BF_PLATE":      pd.to_numeric(row[2], errors="coerce"),
                            "LUNCH_PLATE":   pd.to_numeric(row[3], errors="coerce"),
                            "SNACKS_PLATE":  pd.to_numeric(row[4], errors="coerce"),
                            "DINNER_PLATE":  pd.to_numeric(row[5], errors="coerce"),
                        })
    return pd.DataFrame(rows)


def safe_pct(waste, plate):
    """Waste % capped at 100 to catch bad data."""
    if plate == 0 or pd.isna(plate):
        return 0
    return round(min((waste / plate) * 100, 100))


def validate_files(food_path, plate_path, mess_name):
    """Sanity check: warn if plate and food data look identical."""
    df_f = parse_food_pdf(food_path)
    df_p = parse_plate_pdf(plate_path)
    waste_vals = df_f[["BF_WASTE","LUNCH_WASTE","DINNER_WASTE"]].values.tolist()
    plate_vals = df_p[["BF_PLATE","LUNCH_PLATE","DINNER_PLATE"]].values.tolist()
    if waste_vals == plate_vals:
        print(f"  ⚠  WARNING [{mess_name}]: Plate file looks identical to Food file — check source data!")
        return False
    return True


all_data = []
skipped = []

mess_folders = [
    d for d in os.listdir(ROOT_FOLDER)
    if os.path.isdir(os.path.join(ROOT_FOLDER, d))
    and d.upper() not in {"XLS", "XLS_UPDATED"}   # skip non-mess folders
]

print(f"Found {len(mess_folders)} mess folder(s): {mess_folders}\n")

for folder_name in mess_folders:
    folder_path = os.path.join(ROOT_FOLDER, folder_name)
    pdf_files   = [f for f in os.listdir(folder_path) if f.upper().endswith(".PDF")]

    # Identify food vs plate PDFs by filename keyword
    food_pdfs  = [f for f in pdf_files if "FOOD"  in f.upper() or "WASTAGE" in f.upper()]
    plate_pdfs = [f for f in pdf_files if "PLATE" in f.upper() or "COUNT"   in f.upper()]

    if not food_pdfs or not plate_pdfs:
        print(f"Skipping [{folder_name}]: missing Food or Plate PDF.")
        skipped.append(folder_name)
        continue

    food_path  = os.path.join(folder_path, food_pdfs[0])
    plate_path = os.path.join(folder_path, plate_pdfs[0])

    # Use folder name as mess name (reliable), also verify from PDF header
    mess_name = folder_name.upper()
    pdf_mess  = extract_mess_name_from_pdf(food_path)
    if pdf_mess and pdf_mess != mess_name:
        print(f" [{folder_name}] PDF header says '{pdf_mess}' — using folder name '{mess_name}'")

    print(f"Processing: {mess_name}")
    print(f"  Food  → {food_pdfs[0]}")
    print(f"  Plate → {plate_pdfs[0]}")

    # Validate before processing
    if not validate_files(food_path, plate_path, mess_name):
        skipped.append(mess_name)
        continue

    try:
        df_food  = parse_food_pdf(food_path)
        df_plate = parse_plate_pdf(plate_path)

        if df_food.empty or df_plate.empty:
            print(f"  Empty data extracted — skipping.")
            skipped.append(mess_name)
            continue

        merged = pd.merge(df_food, df_plate, on="MONTH", how="inner")

        if merged.empty:
            print(f"  No matching months after merge — check month format.")
            skipped.append(mess_name)
            continue

        # Calculate waste percentages per meal
        merged["BF_WASTE_%"]     = merged.apply(lambda r: safe_pct(r.BF_WASTE,     r.BF_PLATE),     axis=1)
        merged["LUNCH_WASTE_%"]  = merged.apply(lambda r: safe_pct(r.LUNCH_WASTE,  r.LUNCH_PLATE),  axis=1)
        merged["SNACKS_WASTE_%"] = merged.apply(lambda r: safe_pct(r.SNACKS_WASTE, r.SNACKS_PLATE), axis=1)
        merged["DINNER_WASTE_%"] = merged.apply(lambda r: safe_pct(r.DINNER_WASTE, r.DINNER_PLATE), axis=1)

        # Monthly average across meals that actually have plate data
        def month_avg(row):
            vals = []
            for meal in ["BF", "LUNCH", "SNACKS", "DINNER"]:
                if row[f"{meal}_PLATE"] > 0:
                    vals.append(row[f"{meal}_WASTE_%"])
            return round(sum(vals) / len(vals)) if vals else 0

        merged["MONTH_AVG_WASTE_%"] = merged.apply(month_avg, axis=1)
        merged["MESS_NAME"] = mess_name

        # Reorder columns
        cols = ["MESS_NAME", "MONTH",
                "BF_WASTE", "BF_PLATE", "BF_WASTE_%",
                "LUNCH_WASTE", "LUNCH_PLATE", "LUNCH_WASTE_%",
                "SNACKS_WASTE", "SNACKS_PLATE", "SNACKS_WASTE_%",
                "DINNER_WASTE", "DINNER_PLATE", "DINNER_WASTE_%",
                "MONTH_AVG_WASTE_%"]
        merged = merged[cols]

        all_data.append(merged)
        print(f"  {len(merged)} months extracted.\n")

    except Exception as e:
        print(f"  Error: {e}\n")
        skipped.append(mess_name)

if all_data:
    final_df = pd.concat(all_data, ignore_index=True)

    # Main detailed output
    final_df.to_csv("mess_monthly_waste_analysis.csv", index=False)

    # Yearly summary per mess
    yearly = (
        final_df.groupby("MESS_NAME")
        .agg(
            YEARLY_AVG_WASTE_PCT   = ("MONTH_AVG_WASTE_%", "mean"),
            TOTAL_FOOD_WASTE       = ("BF_WASTE",          "sum"),   # sum of BF as proxy; add others below
            MONTHS_RECORDED        = ("MONTH",              "count"),
        )
        .reset_index()
    )
    # Add proper total waste column
    yearly["TOTAL_FOOD_WASTE"] = final_df.groupby("MESS_NAME").apply(
        lambda g: (g["BF_WASTE"] + g["LUNCH_WASTE"] + g["SNACKS_WASTE"] + g["DINNER_WASTE"]).sum()
    ).values
    yearly["YEARLY_AVG_WASTE_PCT"] = yearly["YEARLY_AVG_WASTE_PCT"].apply(round)
    yearly.to_csv("mess_yearly_summary.csv", index=False)

    print("=" * 50)
    print(f"Done! Processed {len(all_data)} mess(es).")
    if skipped:
        print(f"Skipped: {skipped}")
    print("\nYearly Summary:")
    print(yearly.to_string(index=False))
    print("\nFiles saved:")
    print("  → mess_monthly_waste_analysis.csv")
    print("  → mess_yearly_summary.csv")

else:
    print("No data collected. Check folder path and PDF filenames.")