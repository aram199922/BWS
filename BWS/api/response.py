import os
import sys
import sqlite3

current_directory = os.getcwd()
sys.path.insert(0, current_directory)


def create_response_phone():
    db = sqlite3.connect("testDB.db")
    c = db.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS response_phone (
        id INTEGER PRIMARY KEY,
        Respondent_ID INTEGER,
        Attribute TEXT,
        Block INTEGER,
        Task INTEGER,
        Response INTEGER,
        Age_Range TEXT,
        Gender TEXT
    )
    """
    c.execute(create_table_query)
    db.commit()
    db.close()



def store_response(Respondent_ID, Attributes, Best_Attribute, Worst_Attribute, Block, Task, Age_Range, Gender):
    db = sqlite3.connect("testDB.db")
    c = db.cursor()

    try:
        for Attribute in Attributes:
            Response = 0
            if Attribute == Best_Attribute:
                Response = 1
            elif Attribute == Worst_Attribute:
                Response = -1

            insert_query = "INSERT INTO response_phone (Respondent_ID, Attribute, Block, Task, Response, Age_Range, Gender) VALUES (?, ?, ?, ?, ?, ?, ?)"
            c.execute(insert_query, (Respondent_ID, Attribute, Block, Task, Response, Age_Range, Gender))

        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        c.close()
        db.close()


def get_row_from_survey(table_name, index, block):
    """
    Retrieves a row from the specified table based on its basic index and block.

    Args:
    table_name (str): Name of the table to retrieve the row from.
    index (int): The index of the row to retrieve (0-based).
    block (int): The block number.

    Returns:
    tuple: A tuple containing the values of the row retrieved.
    """
    db = sqlite3.connect("testDB.db")
    c = db.cursor()
    try:
        # Execute query to fetch the row based on index and block
        c.execute(f"SELECT * FROM {table_name} WHERE block = ? LIMIT 1 OFFSET ?", (block, index,))
        row = c.fetchone()
        db.close()
        if row:
            return row  # Return tuple containing row values
        else:
            print(f"No row found at index {index} and block {block} in table {table_name}")
            return None
    except sqlite3.Error as e:
        print(f"Error fetching row from table {table_name}: {e}")
        db.close()
        return None