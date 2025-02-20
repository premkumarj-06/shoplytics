import time
import streamlit as st
import psycopg2 as ps
import os
import pandas as pd

def get_connection():
    DB_NAME = st.secrets["dbname"]
    DB_USER = st.secrets["user"]
    DB_PASS = st.secrets["password"]
    DB_HOST = st.secrets["host"]
    DB_PORT = st.secrets["port"]

    try:
        connection = ps.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        return connection
    except:
        return False

def close_connection(connection):
    if connection:
        connection.close()

def insert_data(product_name, product_category, price, selling_price, profit, payment_type):
    connection = get_connection()
    if not connection:
        return False

    insert_query = """
    INSERT INTO bills_data(name, category, price, selling_price, profit, payment_method) 
    VALUES(%s, %s, %s, %s, %s,%s)
    """
    try:
        cursor = connection.cursor()
        cursor.execute(insert_query, (product_name, product_category, price, selling_price, profit, payment_type))
        connection.commit()
        cursor.close()
        close_connection(connection)
        return True
    except:
        return False

# Queries
previous_day_query = """
    SELECT * FROM bills_data
    WHERE date(created_at) = Date(now()) - 1;
"""
current_day_query = """
    SELECT * FROM bills_data
    WHERE date(created_at) = Date(now());
"""
get_all_data = """
    SELECT * FROM bills_data WHERE date(created_at) = Date(now())
"""

# Function to fetch and render metrics (st.metric)
def fetch_and_render_metrics():
    connection = get_connection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute(previous_day_query)
    previous_day_data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    prev_profit = pd.DataFrame(previous_day_data, columns=columns)["profit"].sum() if previous_day_data else 0

    cursor.execute(current_day_query)
    current_day_data = cursor.fetchall()
    cur_profit = pd.DataFrame(current_day_data, columns=columns)["profit"].sum() if current_day_data else 0

    diff = cur_profit - prev_profit
    st.metric(label=f"Yesterday: {prev_profit} ₹", value=f"Today: {cur_profit} ₹", delta=f"difference: {diff} ₹", border=True)
    cursor.execute("""SELECT * FROM BILLS_DATA""")
    all_data = cursor.fetchall()
    columns = ["ID", "Timestamp", "Product Name", "Category", "Cost Price", "Selling Price", "Profit", "Payment Mode"]
    all_df = pd.DataFrame(all_data, columns=columns)
    all_new_df = all_df[["Category", "Profit", "Selling Price"]]


    total_revenue = all_new_df["Profit"].sum()
    total_turnover = all_new_df["Selling Price"].sum()
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label=f"Yesterday: {prev_profit} ₹", value=f"Today: {cur_profit} ₹", delta=f"difference: {diff} ₹", border=True)
    with col2:
        st.subheader(f"Total Profit: {total_revenue}")
        st.subheader(f"Total TurnOver: {total_turnover}")
    close_connection(connection)

# Function to fetch and render data (st.dataframe)
def fetch_and_render_data():
    connection = get_connection()
    if not connection:
        return

    cursor = connection.cursor()
    cursor.execute(get_all_data)
    table_data_exe = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    if table_data_exe:
        table_data = pd.DataFrame(table_data_exe, columns=columns).set_index('id')
        st.dataframe(table_data)
    else:
        st.write("No data available for today.")

    close_connection(connection)

# Initialize session state for form submission
if "submitted" not in st.session_state:
    st.session_state["submitted"] = False

st.markdown(
    """
    <style>
    div.stButton > button {
        background-color: #007bff !important;  /* Blue color */
        color: white !important;
        border-radius: 5px;
        width: 100%;
        padding: 10px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

product_amount = 0
selling_price = 0
is_entered = False
# Form for bill invoice (above the metrics)
st.write("### Bill Invoice")
with st.form("Bill Invoice", clear_on_submit=True):
    product_name = st.text_input("Product/Service Name")
    product_category = st.selectbox("Product Category", ("Temper glass","Phone Case","Earphone / Headphone", "Combo","Service 🛠","CC Pin", "Battery",
                                                         "CC Board", "V8 Charger","V8 Cable","Power Bank","Bike Mobile Stand","Smart Watch","Iphone Cable", "Type C Cable", "Type C Charger", "Keypad Charger",
                                                         "Neckband","Airpod","Keypad Phone", "Speaker", "Other"))
    product_amount = st.text_input("Price", "")
    selling_price = st.text_input("Selling Price", "")

    payment_method = st.radio(
        "Payment Mode",
        [":blue[Cash 💸]",":blue[Google Pay 📱 ]"],
        captions=[
            " ",
            " ",
        ]
    )
    payment_type = "cash"
    if payment_method == ":blue[Google Pay 📱 ]":
        payment_type = "upi"

    try:
        profit = int(selling_price) - int(product_amount)
    except ValueError:
        profit = 0

    st.write(f"**Profit:** {profit} ₹")

    submit_button = st.form_submit_button("Save", use_container_width=True, type="primary")

    if submit_button and product_name.strip() != "" and product_category.strip() != "":
        is_entered=True
        is_saved = insert_data(product_name, product_category, product_amount, selling_price, profit, payment_type)
        if is_saved:
            st.session_state["submitted"] = True
            st.toast(f"{product_name} Saved to database! 😎", icon="✅")
            time.sleep(1)
            st.rerun()  # Force Streamlit to refresh


# Metrics and Data Table (Always Rendered at the Bottom)
st.write("---")
st.write("### Sales Metrics")
fetch_and_render_metrics()
st.write("### Sales Data")
fetch_and_render_data()
