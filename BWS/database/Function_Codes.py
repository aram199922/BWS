import sqlite3
import pandas as pd
import os

def create_database():
    if not os.path.exists("testDB.db"):
        # Just connect to the database without creating any tables
        db = sqlite3.connect("testDB.db")
        db.close()
        print("Database created successfully.")
    else:
        print("Database already exists.")


def push_flat_file_to_database(file_name, table_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, 'rb') as f:
                df = pd.read_csv(f, encoding='utf-8')
                pandas_to_sql(df, table_name)  # Remove if_exists argument
                print(f"Data from file '{file_name}' appended to SQL table: {table_name}")
        except Exception as e:
            print(f"Error reading file '{file_name}': {e}")
    else:
        print(f"File '{file_name}' not found.")


def insert_attributes(column_name, values_list):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()

    try:
        column_name = column_name.replace(" ", "_")
        # Check if the table exists, if not, create it
        c.execute("CREATE TABLE IF NOT EXISTS Attributes (rowid INTEGER PRIMARY KEY)")
        
        # Check if the column exists in the table schema
        c.execute("PRAGMA table_info(Attributes)")
        columns = [row[1] for row in c.fetchall()]
        
        if column_name not in columns:
            # If the column doesn't exist, create it
            c.execute(f"ALTER TABLE Attributes ADD COLUMN {column_name} TEXT")

        # Get the rowids of rows where the column value is NULL
        c.execute(f"SELECT rowid FROM Attributes WHERE {column_name} IS NULL")
        null_rows = c.fetchall()

        for i, value in enumerate(values_list):
            if i < len(null_rows):
                rowid = null_rows[i][0]
                c.execute(f"UPDATE Attributes SET {column_name} = ? WHERE rowid = ?", (value, rowid))
            else:
                # If there are no more NULL rows, insert a new row
                c.execute(f"INSERT INTO Attributes DEFAULT VALUES")
                rowid = c.lastrowid
                c.execute(f"UPDATE Attributes SET {column_name} = ? WHERE rowid = ?", (value, rowid))
        
        db.commit()
        db.close()
        
        # Return success message
        return "Data inserted successfully"
    except sqlite3.Error as e:
        print(f"Error inserting attributes for column: {column_name} - {e}")
        db.close()
        return "Error inserting attributes"





def get_attributes(column_name):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    try:
        # Assuming column_name is properly formatted
        c.execute(f"SELECT {column_name} FROM Attributes WHERE {column_name} IS NOT NULL")
        result = c.fetchall()
        db.close()
        if result:
            attributes = [row[0] for row in result]
            return attributes
        else:
            print(f"No attributes found for column: {column_name}")
            return None
    except sqlite3.Error as e:
        print(f"Error fetching attributes for column: {column_name} - {e}")
        db.close()
        return None





def read_table(table_name):
    """
    Reads all the information from the specified table in the 'testDB.db' database.

    Args:
    table_name (str): Name of the table to read data from.

    Returns:
    pandas.DataFrame: A DataFrame containing all the data from the table.
    """
    # Connect to the database
    db = sqlite3.connect("testDB.db")
    
    # Read the table into a pandas DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table_name}", db)
    
    # Close the database connection
    db.close()
    
    return df



def update_row_or_column(column_name, to_change, new_value):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()

    try:
        # Check if the table exists, if not, return an error
        c.execute("CREATE TABLE IF NOT EXISTS Attributes (rowid INTEGER PRIMARY KEY)")
        c.execute("PRAGMA table_info(Attributes)")
        columns = [row[1] for row in c.fetchall()]

        # Check if the specified column exists in the table
        if column_name not in columns:
            print(f"Column '{column_name}' does not exist in the table.")
            db.close()
            return

        # Check if 'to_change' is a column name
        if to_change in columns:
            # Rename the specified column
            c.execute(f"ALTER TABLE Attributes RENAME COLUMN {to_change} TO {new_value}")
            print(f"Column '{to_change}' renamed to '{new_value}' successfully.")
        else:
            # Update the specified row with the new value
            c.execute(f"UPDATE Attributes SET {column_name} = ? WHERE {column_name} = ?", (new_value, to_change))
            print(f"Value '{to_change}' in column '{column_name}' updated to '{new_value}' successfully.")

        db.commit()
        db.close()
        return
    
    except sqlite3.Error as e:
        print(f"Error updating row or column: {e}")
        db.close()




def remove_column_or_row(column_name, to_remove):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    
    try:
        # Check if column exists in the table schema
        c.execute(f"PRAGMA table_info(Attributes)")
        columns = [row[1] for row in c.fetchall()]

        # Check if 'column_name' exists in the table
        if column_name not in columns:
            print(f"Column '{column_name}' does not exist in the table.")
            return

        # Check if 'to_remove' is a valid value
        if to_remove in columns:
            # Remove the entire column specified by 'to_remove'
            c.execute(f"ALTER TABLE Attributes DROP COLUMN {to_remove}")
            print(f"Column '{to_remove}' removed successfully.")
        else:
            # Remove the entire row where the specified value is located
            c.execute(f"DELETE FROM Attributes WHERE {column_name} = ?", (to_remove,))
            print(f"Row with value '{to_remove}' from column '{column_name}' removed successfully.")

        db.commit()
        db.close()
    except sqlite3.Error as e:
        print(f"Error removing '{to_remove}': {e}")



def sql_to_pandas(query):
    db = sqlite3.connect("testDB.db")
    df = pd.read_sql_query(query, db)
    db.close()
    return df

def pandas_to_sql(df, table_name, if_exists='replace'):
    db = sqlite3.connect("testDB.db")
    df.to_sql(table_name, db, if_exists=if_exists, index=False)
    db.close()


#currently we dont need this function
#its may be needed in the future so its need some upgrade
def create_table(column_name, attributes):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    column_definitions = ", ".join([f"{attr} TEXT" for attr in attributes])

    create_table_query = f"""CREATE TABLE IF NOT EXISTS Features(
                            {column_name} TEXT,
                            {column_definitions}
                        )"""
    print("Create Table Query:", create_table_query)
    c.execute(create_table_query)
    db.commit()
    db.close()


import sqlite3

def main():
    create_database()
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    db.commit()
    db.close()
    
if __name__ == "__main__":
    main()

