import pandas as pd
import pymysql

# Connect to MySQL
myconnection = pymysql.connect(host='127.0.0.1', user='root', passwd='Chotu', database='redbus')

# Read the CSV file into a DataFrame
csv_file = "C:/Users/ediso/OneDrive/Desktop/Data_science/Project/bus_routes.csv"
df = pd.read_csv(csv_file)

# Define SQL data types for DataFrame columns
sql_data_types = {
    'int64': 'INT',
    'float64': 'FLOAT',
    'object': 'TEXT'
}

# Table name to create and insert data
table_name = "routename"

# Create the table in MySQL
create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        `Bus_Route_Name` TEXT,
        `Route_Link` TEXT
    )
"""
try:
    with myconnection.cursor() as cursor:
        cursor.execute(create_table_query)
    print(f"Table '{table_name}' created or already exists.")
except pymysql.Error as e:
    print(f"Error creating table '{table_name}': {e}")

# Insert data into the table
try:
    with myconnection.cursor() as cursor:
        for index, row in df.iterrows():
            values = (row['Bus_Route_Name'], row['Route_Link'])
            insert_query = f"INSERT INTO {table_name} (`Bus_Route_Name`, `Route_Link`) VALUES (%s, %s)"
            cursor.execute(insert_query, values)
    myconnection.commit()
    print(f"Data inserted into '{table_name}' successfully.")
except pymysql.Error as e:
    print(f"Error inserting data into '{table_name}': {e}")

# Close the connection
myconnection.close()
