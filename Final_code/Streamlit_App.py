import streamlit as st
import pandas as pd
import pymysql

# Function to load data from MySQL
def load_data():
    try:
        connection = pymysql.connect(host='127.0.0.1', user='root', passwd='Chotu', database='redbus')
        query = "SELECT * FROM bus_route"
        df = pd.read_sql(query, connection)
        connection.close()
        return df
    except pymysql.Error as e:
        st.error(f"Error connecting to MySQL: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if there is an error

# Load data
df = load_data()

# Normalize column names by stripping any leading/trailing spaces and converting to a consistent case
df.columns = df.columns.str.strip().str.lower()

# Handle missing values
df['bus_route_name'].fillna('Unknown', inplace=True)
df['bus_type'].fillna('Unknown', inplace=True)
df['departure_time'].fillna('00:00', inplace=True)
df['star_rating'].fillna(0, inplace=True)
df['price'].fillna('0', inplace=True)

# UI for selecting filters
st.sidebar.markdown("## Home")
st.sidebar.markdown('<p style="color:green;font-weight:bold;">Select the Bus</p>', unsafe_allow_html=True)

st.title("Bus Route Information")
st.markdown("### Filter the data to find your preferred bus")

bus_route_name = st.selectbox("Select the Route", [""] + df['bus_route_name'].unique().tolist())
seat_type = st.selectbox("Select the Seat Type", ["", "Sleeper", "Seater", "Semi-Sleeper"])
ac_type = st.selectbox("Select the AC Type", ["", "A/C", "Non A/C"])
ratings = st.selectbox("Select the Ratings", ["", "1 to 2", "2 to 3", "3 to 4", "4 to 5"])
time_range = st.selectbox("Starting time", ["", "00:00 - 06:00", "06:00 - 12:00", "12:00 - 18:00", "18:00 - 24:00"])
fare_range = st.selectbox("Bus Fare Range", ["others", "< 500", "500 - 1000", "1000 - 1500", "> 1500"])

# Helper function to filter time range
def filter_time_range(time_str, time_range):
    hour = int(time_str.split()[0].split(":")[0])
    if time_range == "00:00 - 06:00":
        return 0 <= hour < 6
    elif time_range == "06:00 - 12:00":
        return 6 <= hour < 12
    elif time_range == "12:00 - 18:00":
        return 12 <= hour < 18
    elif time_range == "18:00 - 24:00":
        return 18 <= hour < 24
    return False

# Function to construct SQL query based on filters
def construct_sql_query(df, bus_route_name, seat_type, ac_type, ratings, time_range, fare_range):
    sql_query = "SELECT * FROM bus_route WHERE 1=1"

    if bus_route_name:
        sql_query += f" AND `bus_route_name` = '{bus_route_name}'"
    if seat_type:
        if seat_type.lower() == "sleeper":
            sql_query += " AND (`bus_type` LIKE '%Sleeper%' OR `bus_type` LIKE '%Semi Sleeper%')"
        elif seat_type.lower() == "seater":
            sql_query += " AND `bus_type` LIKE '%Seater%'"
        elif seat_type.lower() == "semi-sleeper":
            sql_query += " AND `bus_type` LIKE '%Semi Sleeper%'"
    if ac_type:
        if ac_type.lower() == "a/c":
            sql_query += " AND (`bus_type` LIKE '%A/c%' OR `bus_type` LIKE '%A/C%')"
        elif ac_type.lower() == "non a/c":
            sql_query += " AND (`bus_type` LIKE '%Non A/c%' OR `bus_type` LIKE '%NON A/C%')"
    if ratings:
        min_rating, max_rating = map(int, ratings.split(" to "))
        sql_query += f" AND `star_rating` >= {min_rating} AND `star_rating` <= {max_rating}"
    if time_range:
        if time_range == "00:00 - 06:00":
            sql_query += " AND HOUR(`departure_time`) >= 0 AND HOUR(`departure_time`) < 6"
        elif time_range == "06:00 - 12:00":
            sql_query += " AND HOUR(`departure_time`) >= 6 AND HOUR(`departure_time`) < 12"
        elif time_range == "12:00 - 18:00":
            sql_query += " AND HOUR(`departure_time`) >= 12 AND HOUR(`departure_time`) < 18"
        elif time_range == "18:00 - 24:00":
            sql_query += " AND HOUR(`departure_time`) >= 18 AND HOUR(`departure_time`) < 24"
    if fare_range != "others":
        if fare_range == "< 500":
            sql_query += " AND CAST(`price` AS UNSIGNED) < 500"
        elif fare_range == "500 - 1000":
            sql_query += " AND CAST(`price` AS UNSIGNED) >= 500 AND CAST(`price` AS UNSIGNED) <= 1000"
        elif fare_range == "1000 - 1500":
            sql_query += " AND CAST(`price` AS UNSIGNED) >= 1000 AND CAST(`price` AS UNSIGNED) <= 1500"
        elif fare_range == "> 1500":
            sql_query += " AND CAST(`price` AS UNSIGNED) > 1500"

    return sql_query

# Construct SQL query based on filters
sql_query = construct_sql_query(df, bus_route_name, seat_type, ac_type, ratings, time_range, fare_range)

# Execute the constructed SQL query
try:
    connection = pymysql.connect(host='127.0.0.1', user='root', passwd='Chotu', database='redbus')
    filtered_data = pd.read_sql(sql_query, connection)
    connection.close()

    # Display filtered data
    st.dataframe(filtered_data)

except pymysql.Error as e:
    st.error(f"Error executing SQL query: {e}")
