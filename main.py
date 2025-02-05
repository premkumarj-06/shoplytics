import streamlit as st
import psycopg2 as ps
from dotenv import load_dotenv
import os





def get_connection():
    load_dotenv()
    # connection = None
    print("Connecting ...")

    # DB_PASS = os.getenv("password")
    # DB_USER = os.getenv("user")
    # DB_PORT = os.getenv("port")
    # DB_HOST = os.getenv("host")

    DB_NAME = st.secrets("dbname")
    DB_USER = st.secrets("user")
    DB_PASS = st.secrets("password")
    DB_HOST = st.secrets("host")
    DB_PORT = st.secrets("port")

    try:
        connection = ps.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        # print("Database connected successfully")
    except:
        # print("Database not connected successfully")
        return False
    if connection:
        print("CONNECTED")
        print("Connection CLOSED")
        return connection

def close_connection(connection):
    connection.close()

def insert_data(product_name, product_category, selling_price, profit):
    connection = get_connection()
    if connection == False:
        pass      
    insert_query = f"""
    INSERT INTO billing_data(product_name, category, price, profit) VALUES(%s, %s, %s, %s)
    """
    data = (product_name, product_category, selling_price, profit,)
    cursor = connection.cursor()
    cursor.execute(insert_query, data)
    connection.commit()
    cursor.close()
    close_connection(connection)
    # return True


# st.sidebar.header('Input')
# selected_type = st.sidebar.selectbox('Select an activity type', ["education", "recreational", "social", "diy", "charity", "cooking", "relaxation", "music", "busywork"])
# with st.form("my_order_invoice"):
st.write("Bill Invoice")
selling_price = 0
profit = 0
product_name = st.text_input("Product/Service Name")
product_category= st.selectbox("Product Category",("Phone Case", "Temper glass", "Earphone", "Speaker", "Other"))
product_amount = st.text_input("Price","0")

selling_price = st.text_input("Selling Price","0")
profit = int(selling_price) - int(product_amount) 
data = [product_name, product_category, selling_price, profit]
st.write("The product name: ", product_name)
st.write("Proft: ", str(profit))
st.write("The product category: ", product_category)
# st.file_uploader("Upload an image")
if (product_name.strip()) != "" or (product_category.strip()) != "":
    st.button("save", on_click=insert_data, args=data)
# else:
#     st.button("save", disabled=True)
