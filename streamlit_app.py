import streamlit as st
import joblib
import pandas as pd
import plotly.express as px
import folium
from streamlit_folium import st_folium
from PIL import Image

# Set up the page configuration
st.set_page_config(page_title="لوحة المعلومات العقارية", layout="wide", initial_sidebar_state="expanded")

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

# Sidebar navigation
st.sidebar.header("انتقل")
selected_page = st.sidebar.radio("Go to", ["نظرة عامة", "رؤى السوق  العقاري", "التنبؤ"])

if selected_page == "نظرة عامة":
    st.title("🏠 لوحة المعلومات العقارية")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("<div class='metric-box'><div class='metric-label'>Waterfront Properties</div><div class='metric-value'>163</div></div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='metric-box'><div class='metric-label'>Total Bedrooms</div><div class='metric-value'>22K</div></div>", unsafe_allow_html=True)
    with col3:
        st.markdown("<div class='metric-box'><div class='metric-label'>Renovated Properties</div><div class='metric-value'>10K</div></div>", unsafe_allow_html=True)

    st.subheader("📊 عدد الغرف")
    bedrooms_data = pd.DataFrame({
        "Bedrooms": ["3 Bedroom", "4 Bedrooms", "5 Bedrooms", "6 Bedrooms", "7 Bedrooms"],
        "Count": [274, 2760, 9824, 6882, 1601, 272]
    })
    fig_bedrooms = px.bar(bedrooms_data, x="Bedrooms", y="Count", color="Bedrooms", title="عدد الغرف في العقار")
    st.plotly_chart(fig_bedrooms)

elif selected_page == "Market Insights":
    st.title("📈 رؤى السوق  العقاري")
    
    DEALS_FILES = {"2022": "selected2022_a.csv", "2023": "selected2023_a.csv", "2024": "selected2024_a.csv"}
    TOTAL_COST_FILE = "deals_total.csv"

    @st.cache_data
    def load_deals_data():
        dataframes = []
        for year, file in DEALS_FILES.items():
            if os.path.exists(file):
                df = pd.read_csv(file)
                df["Year"] = int(year)
                dataframes.append(df)
        return pd.concat(dataframes, ignore_index=True) if dataframes else None

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

    df_deals = load_deals_data()
    df_cost = load_total_cost_data()

    if df_deals is not None and df_cost is not None:
        st.subheader("📊 عدد الصفقات حسب الحي")
        deals_per_district = df_deals.groupby(["District"])["Deal Count"].sum().reset_index()
        fig_deals = px.bar(deals_per_district, x="District", y="Deal Count", color="District", title="Deals per District")
        st.plotly_chart(fig_deals)

        st.subheader("💰 لتكلفة الكلية للصفقات حسب الحي")
        cost_per_district = df_cost.groupby(["District"])["Total Cost"].sum().reset_index()
        fig_cost = px.bar(cost_per_district, x="District", y="Total Cost", color="District", title="Total Cost of Deals")
        st.plotly_chart(fig_cost)
    else:
        st.error("❌ Data files not found!")

elif selected_page == "التنبؤ":
    st.title("🔮 الأسعار التنبؤية")
    with st.form("house_details_form"):
        beds = st.slider("Bedrooms", 3, 7, 3)
        area = st.number_input("Area (sqm)", 150, 12000, 150)
        age = st.number_input("Age of Property", 0, 36, 5)
        street_width = st.selectbox("Street Width (m)", [10, 12, 15, 18,20, 25])
        submitted = st.form_submit_button("Predict Price")
        if submitted:
            new_record = {'beds': beds, 'area': area, 'age': age, 'street_width': street_width}
            predicted_price = model.predict(pd.DataFrame([new_record]))[0]
            st.success(f"Estimated Price: ${predicted_price:,.2f}")

st.markdown("---")
