import sqlite3

def read_measurements_db(db_path):
    # Connect to the SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query to select all data from a table (replace 'your_table_name' with the actual table name)
    cursor.execute("SELECT * FROM ")

    # Fetch all rows from the executed query
    rows = cursor.fetchall()

    # Print the fetched rows
    for row in rows:
        print(row)

    # Close the connection
    conn.close()

# Path to the measurements.db file
db_path = '/Users/aditya_pachpande/Documents/GitHub/New-Code-Layout/Measurements.db'

# Read and print data from the database
read_measurements_db(db_path)