import pandas as pd
import pymysql
import streamlit as st

# Connect to MySQL
try:
    myconnection = pymysql.connect(host='127.0.0.1', user='root', passwd='Chotu', database='redbus')
except pymysql.Error as e:
    st.error(f"Error connecting to MySQL database: {e}")

# Function to fetch and display data from MySQL
def fetch_and_display_data():
    try:
        with myconnection.cursor() as cursor:
            cursor.execute("SELECT `Bus_Route_Name`, `Route_Link` FROM routename")
            data = cursor.fetchall()

            if data:
                routes = {row[0]: row[1] for row in data}

                # Enable scrolling through Bus Route Name with a smaller size
                selected_route = st.selectbox("Select Bus_Route_Name:", options=list(routes.keys()), key='route_select', help='Scroll to select')

                # Display corresponding Route Link next to selected Bus Route Name

                if selected_route in routes:
                    route_link = routes[selected_route]
                    st.write(f"Route_Link: {route_link}")
            else:
                st.write("No data available in the table.")
    except pymysql.Error as e:
        st.error(f"Error fetching data from MySQL: {e}")

# Streamlit UI
def main():
    st.title("Fetch Route_Link")

    # Display the dropdown and route link
    fetch_and_display_data()

# Close the connection
if __name__ == "__main__":
    main()
    try:
        myconnection.close()
    except pymysql.Error as e:
        st.error(f"Error closing MySQL connection: {e}")
