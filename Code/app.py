import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Load Data
df = pd.read_csv('mess_monthly_waste_analysis.csv')
df.columns = df.columns.str.strip()

# 2. Sidebar - User Inputs (The Student App Mockup)
st.sidebar.header("Student Portal (Mockup)")
mess_choice = st.sidebar.selectbox("Select Your Mess", df['MESS_NAME'].unique())
meal_choice = st.sidebar.selectbox("Select Meal to Skip", ["BF", "LUNCH", "DINNER"])
opt_outs = st.sidebar.number_input("How many students are skipping?", min_value=0, value=100)

# 3. Main Dashboard - The Admin View
st.title("🍽️ Eco-Feast Analytics Dashboard")
st.markdown(f"### Current Impact: **₹1.28 Crores** Lost Annually")

# Recipe Reducer Logic
def get_reduction(mess, meal, count):
    plate_col = f"{meal}_PLATE"
    waste_col = f"{meal}_WASTE"
    avg_portion = df[df['MESS_NAME'] == mess][waste_col].mean() / \
                  df[df['MESS_NAME'] == mess][plate_col].mean()
    return round(count * avg_portion, 2)

reduction_kg = get_reduction(mess_choice, meal_choice, opt_outs)

# Actionable Alert for the Chef
st.error(f"⚠️ **CHEF ALERT:** Reduce {meal_choice} production by **{reduction_kg} kg** in {mess_choice} based on student opt-outs.")

# 4. Visualizations
st.subheader("Wastage Trends by Mess")
fig = px.bar(df, x="MESS_NAME", y=f"{meal_choice}_WASTE", color="MONTH", title=f"Annual {meal_choice} Waste per Mess")
st.plotly_chart(fig)

st.subheader("Monthly Waste Forecast")
monthly_trend = df.groupby('MONTH')[[f'BF_WASTE', 'LUNCH_WASTE', 'DINNER_WASTE']].sum().sum(axis=1)
st.line_chart(monthly_trend)