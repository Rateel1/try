import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium

# Set up the page configuration
st.set_page_config(page_title="لوحة المعلومات العقارية ", layout="wide", initial_sidebar_state="collapsed")

# Load the trained model
@st.cache_resource
def load_model():
    return joblib.load("lgbm.joblib")

model = load_model()

# Layout with 3 columns and 2 rows
st.title("🏠 لوحة المعلومات العقارية ")

# First Row: Map, Specification & Prediction
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("📍 اختر الموقع")
    riyadh_lat, riyadh_lng = 24.7136, 46.6753
    m = folium.Map(location=[riyadh_lat, riyadh_lng], zoom_start=11)
    st_folium(m, width=500, height=400)

with col2:
    st.subheader("🏠 أدخل تفاصيل المنزل")
    beds = st.slider("عدد غرف النوم 🛏️", 3, 7, 3)
    area = st.number_input("المساحة (متر مربع) 📏", 150.0, 12000.0, 150.0)
    age = st.number_input("عمر العقار 🗓️", 0, 36, 5)
    street_width = st.selectbox("عرض الشارع (متر) 🛣️", [10, 12, 15, 18, 20, 25], index=2)

with col3:
    st.subheader("🔮 توقع السعر")
    if st.button("توقع السعر"):
        new_record = {'beds': beds, 'area': area, 'age': age, 'street_width': street_width}
        predicted_price = model.predict(pd.DataFrame([new_record]))[0]
        st.success(f"السعر التقريبي: ريال {predicted_price:,.2f}")

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
    st.subheader("📊 تأثير الخصائص على السعر")
    if df_features is not None:
        fig_features = px.bar(df_features, x="Importance", y="Feature", orientation="h", title="Feature Importance", color="Importance")
        st.plotly_chart(fig_features)
    else:
        st.warning("❌ بيانات تأثير الخصائص غير متوفرة!")

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

year_selected = st.sidebar.slider("📅 اختر السنة", 2022, 2024, 2023)

with col5:
    st.subheader("📊 عدد الصفقات")
    if df_deals is not None:
        df_filtered = df_deals[df_deals["Year"] == year_selected]
        fig_deals = px.bar(df_filtered, x="District", y="Deal Count", color="Year", title="عدد الصفقات حسب الحي",
                           hover_data={"District": True, "Deal Count": True, "Year": True})
        st.plotly_chart(fig_deals)
    else:
        st.warning("❌ بيانات الصفقات غير متوفرة!")

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
        return df
    return None

df_cost = load_total_cost_data()

with col6:
    st.subheader("💰 التكلفة الكلية للصفقات")
    if df_cost is not None:
        df_cost_filtered = df_cost[df_cost["Year"] == year_selected]
        fig_cost = px.bar(df_cost_filtered, x="District", y="Total Cost", color="Year", title="التكلفة الكلية للصفقات",
                          hover_data={"District": True, "Total Cost": True, "Year": True})
        st.plotly_chart(fig_cost)
    else:
        st.warning("❌ بيانات التكلفة غير متوفرة!")

st.markdown("---")
