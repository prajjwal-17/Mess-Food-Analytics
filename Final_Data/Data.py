import pandas as pd

# Load your CSV
df = pd.read_csv('D:\Mess-Food-Analytics\Data\mess_monthly_waste_analysis.csv')

# Step 1: Standardize the Menu (Injecting standard hostel dishes for the demo)
# In a real app, the admin would upload this. For now, we map by meal type.
menu_map = {
    'BF': 'Idli/Dosa/Poha/Bread/Pongal/Chappathi/Vada/Upma/Poori/Potato Masala',
    'LUNCH': 'Rice/Dal/Sabzi/Curd/Palak Panneer/Chicken Curry/Kashmiri Dum Aloo/Dal Tadka,',
    'SNACKS': 'Tea/Biscuits/Samosa/Pav Baji,Pani Poori/Bonda',
    'DINNER': 'Roti/Paneer/Chicken/Rice/Jeera Dal/Panjabi Paratha/Steamed Rice/Vegetable Curry/Veg Kuruma',
}

# Step 2: Transform to Long Format
# We will create a clean list of [Mess, Month, Meal, Waste, Plates, Dishes]
processed_data = []

for index, row in df.iterrows():
    for meal in ['BF', 'LUNCH', 'SNACKS', 'DINNER']:
        processed_data.append({
            'Mess': row['MESS_NAME'],
            'Month': row['MONTH'],
            'Meal': meal,
            'Waste_KG': row[f'{meal}_WASTE'],
            'Plates': row[f'{meal}_PLATE'],
            'Waste_Percent': row[f'{meal}_WASTE_%'],
            'Estimated_Dish': menu_map[meal]
        })

master_df = pd.DataFrame(processed_data)
master_df.to_csv('final_training_data.csv', index=False)
print("Phase 1 Complete: Dataset is now 'AI-Ready'.")