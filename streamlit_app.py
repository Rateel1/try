import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Set up the page configuration
st.set_page_config(page_title="Property Management Dashboard", layout="wide", initial_sidebar_state="expanded")

# Load the trained model
@st.cache_resource
def load_model():
    return joblib.load("lgbm.joblib")

model = load_model()

# Layout with 3 columns and 2 rows
st.title("🏠 Property Management Dashboard")

# First Row: Map, Specification & Prediction
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("📍 Select Location")
    m = folium.Map(location=[24.7136, 46.6753], zoom_start=11)
    st_folium(m, width=500, height=400)

with col2:
    st.subheader("🏠 Property Specification")
    beds = st.slider("Bedrooms", 1, 7, 3)
    area = st.number_input("Area (sqm)", 50, 500, 100)
    age = st.number_input("Age of Property", 0, 50, 5)
    street_width = st.selectbox("Street Width (m)", [10, 12, 15, 20, 25])

with col3:
    st.subheader("🔮 Predict Price")
    if st.button("Predict Price"):
        new_record = {'beds': beds, 'area': area, 'age': age, 'street_width': street_width}
        predicted_price = model.predict(pd.DataFrame([new_record]))[0]
        st.success(f"Estimated Price: ${predicted_price:,.2f}")

# Second Row: Feature Importance, Deals Count, Deals Cost
col4, col5, col6 = st.columns([1, 1, 1])

# Feature Importance
FEATURE_IMPORTANCE_FILE = "feature_importance.csv"
@st.cache_data
def load_feature_importance_data():
    if os.path.exists(FEATURE_IMPORTANCE_FILE):
        df = pd.read_csv(FEATURE_IMPORTANCE_FILE)
        return df
    return None

df_features = load_feature_importance_data()

with col4:
    st.subheader("📊 Feature Importance")
    if df_features is not None:
        fig_features = px.bar(df_features, x="Importance", y="Feature", orientation="h", title="Feature Importance", color="Importance")
        st.plotly_chart(fig_features)
    else:
        st.warning("Feature importance data not found!")

# Deals Count
DEALS_FILES = {"2022": "selected2022_a.csv", "2023": "selected2023_a.csv", "2024": "selected2024_a.csv"}
@st.cache_data
def load_deals_data():
    dataframes = []
    for year, file in DEALS_FILES.items():
        if os.path.exists(file):
            df = pd.read_csv(file)
            df["Year"] = int(year)
            dataframes.append(df)
    return pd.concat(dataframes, ignore_index=True) if dataframes else None

df_deals = load_deals_data()

year_selected = st.sidebar.slider("Select Year", 2022, 2024, 2023)

with col5:
    st.subheader("📊 Deals Count")
    if df_deals is not None:
        df_filtered = df_deals[df_deals["Year"] == year_selected]
        fig_deals = px.bar(df_filtered, x="District", y="Deal Count", color="Year", title="Deals Count by District",
                           hover_data={"District": True, "Deal Count": True, "Year": True})
        st.plotly_chart(fig_deals)
    else:
        st.warning("Deals data not available!")

# Deals Cost
TOTAL_COST_FILE = "deals_total.csv"
@st.cache_data
def load_total_cost_data():
    if os.path.exists(TOTAL_COST_FILE):
        df = pd.read_csv(TOTAL_COST_FILE)
        first_col = df.columns[0]
        df = df.melt(id_vars=[first_col], var_name="Year", value_name="Total Cost")
        df.rename(columns={first_col: "District"}, inplace=True)
        df["Year"] = df["Year"].astype(int)
        retu
