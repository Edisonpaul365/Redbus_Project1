import pandas as pd
import pymysql
from datetime import datetime

# Connect to MySQL
try:
    myconnection = pymysql.connect(host='127.0.0.1', user='root', passwd='Chotu', database='redbus')
    print("MySQL connection established.")
except pymysql.Error as e:
    print(f"Error connecting to MySQL: {e}")
    exit(1)

# Read the CSV file into a DataFrame
csv_file = "C:/Users/ediso/OneDrive/Desktop/Data_science/Project/bus_routes.csv"
try:
    df = pd.read_csv(csv_file, encoding='utf-8')  # Adjust encoding if needed
    print("CSV file successfully loaded.")
except Exception as e:
    print(f"Error loading CSV file: {e}")
    exit(1)  # Exit the script if there's an error loading the CSV

# Print column names to check for discrepancies
print("Columns in the CSV file:", df.columns)

# Normalize column names by stripping any leading/trailing spaces and converting to a consistent case
df.columns = df.columns.str.strip().str.lower()

# Check for 'departure_time' and 'reaching_time' in columns
if 'departure_time' not in df.columns or 'reaching_time' not in df.columns:
    print("Column names 'departure_time' and/or 'reaching_time' not found in the CSV file.")
    exit(1)

# Table name to create and insert data
table_name = "bus_route"

# Create the table in MySQL
create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        `id` INT AUTO_INCREMENT PRIMARY KEY,
        `bus_route_name` TEXT,
        `bus_name` TEXT,
        `bus_type` TEXT,
        `departure_time` DATETIME,
        `duration` TEXT,
        `reaching_time` DATETIME,
        `star_rating` FLOAT,
        `price` DECIMAL(10, 2),
        `seat_availability` TEXT
    )
"""
try:
    with myconnection.cursor() as cursor:
        cursor.execute(create_table_query)
    print(f"Table '{table_name}' created or already exists.")
except pymysql.Error as e:
    print(f"Error creating table '{table_name}': {e}")
    myconnection.close()
    exit(1)

# Insert data into the table
try:
    with myconnection.cursor() as cursor:
        for index, row in df.iterrows():
            try:
                # Parse the time strings directly into DATETIME format for MySQL
                departure_time = datetime.strptime(row['departure_time'], "%Y-%m-%d %H:%M:%S") if pd.notnull(row['departure_time']) else None
                reaching_time = datetime.strptime(row['reaching_time'], "%Y-%m-%d %H:%M:%S") if pd.notnull(row['reaching_time']) else None

                # Convert star_rating to float, handling non-numeric values
                try:
                    star_rating = float(row['star_rating']) if pd.notnull(row['star_rating']) else None
                except ValueError:
                    star_rating = None

                # Handle non-numeric prices
                try:
                    price = float(row['price']) if pd.notnull(row['price']) else None
                except ValueError:
                    price = None

                # Replace NaN values with None for all other columns
                values = (
                    row['bus_route_name'] if pd.notnull(row['bus_route_name']) else None, 
                    row['bus_name'] if pd.notnull(row['bus_name']) else None, 
                    row['bus_type'] if pd.notnull(row['bus_type']) else None, 
                    departure_time,
                    row['duration'] if pd.notnull(row['duration']) else None, 
                    reaching_time,
                    star_rating,
                    price, 
                    row['seat_availability'] if pd.notnull(row['seat_availability']) else None
                )
                insert_query = f"""
                    INSERT INTO {table_name} 
                    (`bus_route_name`, `bus_name`, `bus_type`, `departure_time`, `duration`, 
                    `reaching_time`, `star_rating`, `price`, `seat_availability`) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, values)
            except Exception as e:
                print(f"Error inserting row {index + 1}: {e}")
    myconnection.commit()
    print(f"Data inserted into '{table_name}' successfully.")
except pymysql.Error as e:
    print(f"Error inserting data into '{table_name}': {e}")
finally:
    myconnection.close()
    print("MySQL connection closed.")
