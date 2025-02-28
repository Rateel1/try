import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Set up the page configuration
st.set_page_config(page_title="Property Management Dashboard", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for styling
st.markdown("""
<style>
.stApp {
    background-color: #f8f9fa;
}
.stButton>button {
    color: #ffffff;
    background-color: #e63946;
    border-radius: 8px;
    padding: 10px 20px;
    font-size: 16px;
}
.metric-box {
    background-color: #ffffff;
    padding: 15px;
    border-radius: 10px;
    box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    text-align: center;
    margin-bottom: 10px;
}
.metric-label {
    font-size: 18px;
    color: #555;
}
.metric-value {
    font-size: 30px;
    font-weight: bold;
    color: #e63946;
}
</style>
""", unsafe_allow_html=True)

# Load the trained model
@st.cache_resource
def load_model():
    return joblib.load("lgbm.joblib")

model = load_model()

# Layout with 3 columns
col1, col2, col3 = st.columns([1, 1, 1])

# First row
with col1:
    st.subheader("📍 Select Location")
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=11)
    st_folium(m, width=400, height=300)

with col2:
    st.subheader("🏠 Property Specification & Prediction")
    beds = st.slider("Bedrooms", 1, 7, 3)
    area = st.number_input("Area (sqm)", 50, 500, 100)
    age = st.number_input("Age of Property", 0, 50, 5)
    street_width = st.selectbox("Street Width (m)", [10, 12, 15, 20, 25])
    if st.button("Predict Price"):
        new_record = {'beds': beds, 'area': area, 'age': age, 'street_width': street_width}
        predicted_price = model.predict(pd.DataFrame([new_record]))[0]
        st.success(f"Estimated Price: ${predicted_price:,.2f}")

with col3:
    st.subheader("📊 Deals Count")
    year_selected = st.slider("Select Year", 2022, 2024, 2023)
    # Load deal data
    DEALS_FILES = {"2022": "selected2022_a.csv", "2023": "selected2023_a.csv", "2024": "selected2024_a.csv"}
    @st.cache_data
    def load_deals_data():
        file = DEALS_FILES[str(year_selected)]
        if file:
            return pd.read_csv(file)
        return None
    df_deals = load_deals_data()
    if df_deals is not None:
        st.dataframe(df_deals.head())
    else:
        st.warning("No data available.")

# Second row
col4, col5 = st.columns([1, 1])

with col4:
    st.subheader("📈 Properties & Prices")
    properties_data = pd.DataFrame({
        "Year": [2020, 2021, 2022, 2023, 2024],
        "Properties": [1000, 1500, 2000, 2500, 3000]
    })
    fig_properties = px.line(properties_data, x="Year", y="Properties", title="Properties Built Over Years")
    st.plotly_chart(fig_properties)

with col5:
    st.subheader("💰 Cost of Deals")
    cost_data = pd.DataFrame({
        "District": ["A", "B", "C", "D"],
        "Total Cost": [500000, 700000, 800000, 600000]
    })
    fig_cost = px.bar(cost_data, x="District", y="Total Cost", color="District", title="Total Cost of Deals per District")
    st.plotly_chart(fig_cost)

st.markdown("---")
