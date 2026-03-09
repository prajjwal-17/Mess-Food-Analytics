import pandas as pd

# Load your data
df = pd.read_csv('D:\Code\mess_monthly_waste_analysis.csv')

# Clean column names (removes leading/trailing spaces)
df.columns = df.columns.str.strip()

print("Detected Columns:", df.columns.tolist())

# Logic to find the correct columns even if named differently
waste_col = [col for col in df.columns if 'waste' in col.lower() or 'wastage' in col.lower()][0]
mess_col = [col for col in df.columns if 'mess' in col.lower()][0]

# 1. Total Annual Impact
total_kg = df[waste_col].sum()

# 2. Identify the "Problem Child" Mess
mess_stats = df.groupby(mess_col)[waste_col].sum().sort_values(ascending=False)

# 3. Financial Impact (Avg cost of ₹40 per kg)
financial_loss = total_kg * 40

print(f"\n--- DATA-BACKED INSIGHTS FOR SLIDE 5 ---")
print(f"Total Food Wasted: {total_kg:,.2f} kg")
print(f"Estimated Financial Loss: ₹{financial_loss:,.2f}")
print(f"Highest Wastage Mess: {mess_stats.index[0]} ({mess_stats.iloc[0]:,.2f} kg)")



def recipe_reducer(mess_name, meal_type, opt_out_count):
    """
    Calculates how much food weight to reduce based on student opt-outs.
    meal_type: 'BF', 'LUNCH', 'SNACKS', or 'DINNER'
    """
    # Calculate average waste per plate for that mess/meal from your data
    plate_col = f"{meal_type}_PLATE"
    waste_col = f"{meal_type}_WASTE"
    
    avg_portion_kg = df[df['MESS_NAME'] == mess_name][waste_col].mean() / \
                     df[df['MESS_NAME'] == mess_name][plate_col].mean()
    
    reduction_kg = opt_out_count * avg_portion_kg
    return round(reduction_kg, 2)

# Example Usage for the Pitch:
# "If 100 students in SANNASI opt-out of Lunch today..."
saved_amount = recipe_reducer('SANNASI', 'LUNCH', 100)
print(f"Prediction Engine: Reduce Lunch production by {saved_amount} kg for 100 opt-outs.")