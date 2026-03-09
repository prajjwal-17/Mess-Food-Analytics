from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import json

app = FastAPI()

# Enable CORS so your React frontend can talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- PHASE 1 DATA LOADING ---
# Load the CSV you cleaned earlier
df = pd.read_csv('../Data/mess_monthly_waste_analysis.csv')

# Simulated state for the hackathon (In a real app, this is a database)
# This tracks how many students clicked "SKIP" on the app today
live_skips = {
    "D-MESS": 0, "J-MESS": 0, "MEENAKSHI": 0, 
    "SANNASI": 0, "SENBAGAM": 0, "STAFF MESS": 0
}

# --- ENDPOINTS ---

@app.get("/analytics/summary")
def get_summary():
    """Returns the big numbers for Prajjwal's Admin Dashboard"""
    # 1. Calculate Total Waste KG across all meals and months
    waste_cols = ['BF_WASTE', 'LUNCH_WASTE', 'DINNER_WASTE']
    total_waste = df[waste_cols].sum().sum()
    
    # 2. Financial Loss (Waste KG * ₹40)
    total_loss = total_waste * 40
    
    # 3. Mess Efficiency Ranking
    mess_stats = df.groupby('MESS_NAME')['MONTH_AVG_WASTE_%'].mean().to_dict()
    
    return {
        "total_waste_kg": round(total_waste, 2),
        "total_financial_loss_inr": round(total_loss, 2),
        "co2_emissions_tonnes": round(total_waste * 2.5 / 1000, 2), # Environmental Impact
        "mess_rankings": mess_stats
    }

@app.get("/forecast/{mess_name}")
def get_forecast(mess_name: str):
    """The 'Smart Headcount' Logic"""
    mess_name = mess_name.upper()
    if mess_name not in live_skips:
        return {"error": "Mess not found"}

    # 1. Get Historical Average Plates for Lunch (using March as current month)
    # We divide by 30 to get a daily average from the monthly data
    monthly_data = df[(df['MESS_NAME'] == mess_name) & (df['MONTH'] == 'Mar-2024')]
    avg_daily_plates = monthly_data['LUNCH_PLATE'].values[0] / 30
    
    # 2. Apply the "Smart" adjustment
    skips = live_skips[mess_name]
    smart_headcount = (avg_daily_plates - skips) * 1.10 # 10% safety buffer
    
    return {
        "mess": mess_name,
        "historical_avg": round(avg_daily_plates),
        "live_skips": skips,
        "smart_headcount": round(smart_headcount),
        "savings_today_inr": round(skips * 35) # Estimated saving per plate
    }

@app.post("/skip-meal/{mess_name}")
def register_skip(mess_name: str):
    """Receives the signal from Shashvat's Student App"""
    mess_name = mess_name.upper()
    if mess_name in live_skips:
        live_skips[mess_name] += 1
        return {"status": "success", "current_skips": live_skips[mess_name]}
    return {"status": "error"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)