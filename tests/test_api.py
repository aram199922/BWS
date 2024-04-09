#Seeing all our tables ---------------------------------------------
import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('testDB.db')
cursor = conn.cursor()

# Query the sqlite_master table to get a list of table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

# Print the table names
for table in tables:
    print(table[0])

# Close the connection
conn.close()