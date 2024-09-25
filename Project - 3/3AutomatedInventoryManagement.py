import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
from sklearn.linear_model import LinearRegression
import numpy as np

# Initialize inventory
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame(columns=["Item Name", "Quantity", "Price", "URL", "Sales History"])

# Function to scrape product data
def scrape_product_data(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Example: Extracting product name, price, and quantity from a hypothetical website
    products = []
    for product in soup.find_all(class_='product-item'):
        name = product.find(class_='product-title').get_text()
        price = float(product.find(class_='product-price').get_text().replace('$', ''))
        quantity = int(product.find(class_='product-quantity').get_text())
        products.append((name, quantity, price))
    return products

# Predict demand using historical sales data
def forecast_demand(sales_history):
    if len(sales_history) < 2:
        return 0  # Not enough data to forecast
    X = np.array(range(len(sales_history))).reshape(-1, 1)
    y = np.array(sales_history).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, y)
    next_month = np.array([[len(sales_history)]])
    return model.predict(next_month)[0][0]

# Streamlit UI
st.title("Automated Inventory Management System")

menu = ["Add Item", "View Inventory", "Scrape Product Data", "Forecast Demand"]
choice = st.sidebar.selectbox("Select Operation", menu)

if choice == "Add Item":
    st.subheader("Add Item to Inventory")
    item_name = st.text_input("Item Name")
    quantity = st.number_input("Quantity", min_value=0)
    price = st.number_input("Price", min_value=0.0)
    url = st.text_input("Product URL")
    
    if st.button("Add"):
        new_item = pd.DataFrame([[item_name, quantity, price, url, []]], columns=["Item Name", "Quantity", "Price", "URL", "Sales History"])
        st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
        st.success(f"{item_name} added to inventory.")
        st.markdown(f"[View Product]({url})", unsafe_allow_html=True)

elif choice == "View Inventory":
    st.subheader("Current Inventory")
    if not st.session_state.inventory.empty:
        inventory_df = st.session_state.inventory
        for idx, row in inventory_df.iterrows():
            st.write(f"**Item Name**: {row['Item Name']}")
            st.write(f"**Quantity**: {row['Quantity']}")
            st.write(f"**Price**: ${row['Price']:.2f}")
            st.markdown(f"[View Product]({row['URL']})", unsafe_allow_html=True)
            st.write(f"**Sales History**: {row['Sales History']}")
            st.write("---")
    else:
        st.write("No items in inventory.")

elif choice == "Scrape Product Data":
    st.subheader("Scrape Product Data")
    url = st.text_input("Enter URL of the e-commerce site")
    
    if st.button("Scrape"):
        products = scrape_product_data(url)
        for name, quantity, price in products:
            new_item = pd.DataFrame([[name, quantity, price, url, []]], columns=["Item Name", "Quantity", "Price", "URL", "Sales History"])
            st.session_state.inventory = pd.concat([st.session_state.inventory, new_item], ignore_index=True)
        st.success("Product data scraped and added to inventory.")

elif choice == "Forecast Demand":
    st.subheader("Forecast Demand for Items")
    if not st.session_state.inventory.empty:
        item_name = st.selectbox("Select Item", st.session_state.inventory["Item Name"].tolist())
        
        if st.button("Forecast"):
            idx = st.session_state.inventory[st.session_state.inventory["Item Name"] == item_name].index[0]
            sales_history = st.session_state.inventory.at[idx, "Sales History"]
            forecast = forecast_demand(sales_history)
            st.success(f"Forecasted demand for {item_name} is: {forecast:.2f} units.")
    else:
        st.write("No items in inventory.")

# Option to update product details
if choice == "View Inventory" and not st.session_state.inventory.empty:
    st.subheader("Update Item Details")
    item_name = st.selectbox("Select Item to Update", st.session_state.inventory["Item Name"].tolist())
    
    if st.button("Load Item"):
        idx = st.session_state.inventory[st.session_state.inventory["Item Name"] == item_name].index[0]
        current_quantity = st.session_state.inventory.at[idx, "Quantity"]
        current_price = st.session_state.inventory.at[idx, "Price"]
        new_quantity = st.number_input("New Quantity", value=current_quantity, min_value=0)
        new_price = st.number_input("New Price", value=current_price, min_value=0.0)

        if st.button("Update"):
            st.session_state.inventory.at[idx, "Quantity"] = new_quantity
            st.session_state.inventory.at[idx, "Price"] = new_price
            st.success(f"{item_name} updated successfully.")

