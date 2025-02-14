# Upload CSV file
uploaded_file = st.file_uploader("table2022", type=["csv"])

if uploaded_file is not None:
    # Read the uploaded CSV
    df = pd.read_csv(uploaded_file)

    # Ensure column names are correct
    st.write("عدد الصفقات 2022", df.head())

    # Create an interactive bar chart
    fig = px.bar(
        df,
        x=df.columns[0],  # Replace with correct column name if needed
        y=df.columns[1],  # Replace with correct column name if needed
        title="Real Estate Transactions (2022)",
        labels={"x": "الحي", "y": " عدد الصفقات"},
        text_auto=True
    )

    # Show chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)
