import sqlite3
import pandas as pd
import os

def create_database():
    if not os.path.exists("testDB.db"):
        db = sqlite3.connect("testDB.db")
        db.close()
        print("Database created successfully.")
    else:
        print("Database already exists.")

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



def get_attributes( table_name,company_name):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    try:
        column_name = company_name.replace(" ", "_")
        print("Generated Column Name:", column_name)
        c.execute(f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL")
        result = c.fetchall()
        print("Fetched Rows:", result)
        db.close()
        if result:
            attributes = [row[0] for row in result]
            return attributes
        else:
            print(f"No attributes found for company: {company_name}")
            return None
    except sqlite3.Error as e:
        print(f"Error fetching attributes for company: {company_name} - {e}")
        db.close()
        return None

def insert_attributes(table_name, column_name, values_list):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()

    try:
        c.execute(f"SELECT {column_name} FROM {table_name} WHERE {column_name} IS NOT NULL LIMIT 1")
    except sqlite3.OperationalError:
        c.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} TEXT")

    # Get the rowids of rows where the column value is NULL
    c.execute(f"SELECT rowid FROM {table_name} WHERE {column_name} IS NULL")
    null_rows = c.fetchall()

    for i, value in enumerate(values_list):
        if i < len(null_rows):
            rowid = null_rows[i][0]
            c.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE rowid = ?", (value, rowid))
        else:
            # If there are no more NULL rows, insert a new row
            c.execute(f"INSERT INTO {table_name} DEFAULT VALUES")
            rowid = c.lastrowid
            c.execute(f"UPDATE {table_name} SET {column_name} = ? WHERE rowid = ?", (value, rowid))

    db.commit()
    db.close()
    
    # Return success message
    return "Data inserted successfully"


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


def sql_to_pandas(query):
    db = sqlite3.connect("testDB.db")
    df = pd.read_sql_query(query, db)
    db.close()
    return df

def pandas_to_sql(df, table_name, if_exists='replace'):
    db = sqlite3.connect("testDB.db")
    df.to_sql(table_name, db, if_exists=if_exists, index=False)
    db.close()


def main():
    create_database()
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    db.commit()
    db.close()

    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    c.execute("PRAGMA table_info(Features)")
    columns = [column[1] for column in c.fetchall()]
    db.close()
if __name__ == "__main__":
    main()
