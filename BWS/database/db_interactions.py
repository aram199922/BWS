import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

import sqlite3
import pandas as pd

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


def insert_rows(table_name, df):
    """
    Inserts rows into the specified table.

    Args:
    table_name (str): Name of the table to insert rows into.
    df (DataFrame): Pandas DataFrame containing rows to insert.

    Returns:
    str: A message indicating the success or failure of the operation.
    """
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    try:
        # Get the number of columns in the table
        c.execute(f"PRAGMA table_info({table_name})")
        table_columns = [row[1] for row in c.fetchall()]
        print("Table Columns:", table_columns)  # Add this line
        
        # Check if the number of columns in the DataFrame matches the number of columns in the table
        print("DataFrame Columns:", df.columns)  # Add this line
        if len(df.columns) != len(table_columns):
            db.close()
            return f"Number of columns in DataFrame ({len(df.columns)}) doesn't match the number of columns in the table ({len(table_columns)})."


        # Convert all values in the DataFrame to strings
        df = df.applymap(str)

        # Check for non-convertible values
        for column in df.columns:
            if not df[column].apply(lambda x: isinstance(x, str)).all():
                db.close()
                return f"Non-convertible values found in column '{column}'."

        # Insert data into the specified table
        c.executemany(f"INSERT INTO {table_name} VALUES ({','.join(['?' for _ in range(len(table_columns))])})", df.values.tolist())
        db.commit()
        db.close()
        return "Rows inserted successfully."
    except sqlite3.Error as e:
        db.rollback()
        db.close()
        return f"Error inserting rows into table {table_name}: {e}"





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


def get_row_from_survey(table_name, index):
    """
    Retrieves a row from the specified table based on its basic index.

    Args:
    table_name (str): Name of the table to retrieve the row from.
    index (int): The index of the row to retrieve (0-based).

    Returns:
    tuple: A tuple containing the values of the row retrieved.
    """
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    try:
        # Execute query to fetch the row based on index
        c.execute(f"SELECT * FROM {table_name} LIMIT 1 OFFSET ?", (index,))
        row = c.fetchone()
        db.close()
        if row:
            return row  # Return tuple containing row values
        else:
            print(f"No row found at index {index} in table {table_name}")
            return None
    except sqlite3.Error as e:
        print(f"Error fetching row from table {table_name}: {e}")
        db.close()
        return None



def insert_rows(table_name, df):
    """
    Inserts rows into the specified table.

    Args:
    table_name (str): Name of the table to insert rows into.
    df (DataFrame): Pandas DataFrame containing rows to insert.

    Returns:
    str: A message indicating the success or failure of the operation.
    """
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    try:
        # Check if the table exists
        c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?;", (table_name,))
        table_exists = c.fetchone()
        if not table_exists:
            db.close()
            return f"Table '{table_name}' does not exist."

        # Get the number of columns in the table
        c.execute(f"PRAGMA table_info({table_name})")
        table_columns = [row[1] for row in c.fetchall()]

        # Check if the number of columns in the DataFrame matches the number of columns in the table
        if len(df.columns) != len(table_columns):
            db.close()
            return f"Number of columns in DataFrame ({len(df.columns)}) doesn't match the number of columns in the table ({len(table_columns)})."

        # Convert all values in the DataFrame to strings
        df = df.applymap(str)

        # Construct the SQL query dynamically based on the number of columns
        placeholders = ','.join(['?'] * len(table_columns))
        query = f"INSERT INTO {table_name} VALUES ({placeholders})"
        
        # Insert data into the specified table
        c.executemany(query, df.values.tolist())
        db.commit()
        db.close()
        return "Rows inserted successfully."
    except sqlite3.Error as e:
        db.rollback()
        db.close()
        return f"Error inserting rows into table {table_name}: {e}"



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


def main():
    create_database()
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    db.commit()
    db.close()
    
if __name__ == "__main__":
    main()

