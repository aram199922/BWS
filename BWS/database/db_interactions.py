import os
import sys
import sqlite3
import pandas as pd
import logging
from ..logger import *

# current_directory = os.getcwd()
# sys.path.insert(0, current_directory)


logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


class SqlHandle:
    def __init__(self, db_name="testDB.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def close(self):
        self.cursor.close()
        self.connection.close()
        logger.info('the connection has been closed')

    def create_database(self):
        if not os.path.exists(self.db_name):
            logger.info('Database has been created')
            print("Database created successfully.")
            logger.info('Database has been created')
        else:
            print("Database already exists.")
            logger.warning('You are trying to create a database that already exists')
        self.close()


    def push_flat_file_to_database(self, file_name, table_name):
        if os.path.exists(file_name):
            try:
                with open(file_name, 'rb') as f:
                    df = pd.read_csv(f, encoding='utf-8')
                    self.pandas_to_sql(df, table_name)  # Remove if_exists argument
                    print(f"Data from file '{file_name}' appended to SQL table: {table_name}")
            except Exception as e:
                print(f"Error reading file '{file_name}': {e}")
                logger.info('File has been pushed')
        else:
            print(f"File '{file_name}' not found.")
            logger.warning('The file you are trying to push cannot be found')
        self.close()
    

    def insert_attributes(self, column_name, values_list):
        try:
            column_name = column_name.replace(" ", "_")
            self.cursor.execute("CREATE TABLE IF NOT EXISTS Attributes (rowid INTEGER PRIMARY KEY)")
            self.cursor.execute("PRAGMA table_info(Attributes)")
            columns = [row[1] for row in self.cursor.fetchall()]
            logger.info('Attributes table has been created')
            
            if column_name not in columns:
                # If the column doesn't exist, create it
                self.cursor.execute(f"ALTER TABLE Attributes ADD COLUMN {column_name} TEXT")

            # Get the rowids of rows where the column value is NULL
            self.cursor.execute(f"SELECT rowid FROM Attributes WHERE {column_name} IS NULL")
            null_rows = self.cursor.fetchall()

            for i, value in enumerate(values_list):
                if i < len(null_rows):
                    rowid = null_rows[i][0]
                    self.cursor.execute(f"UPDATE Attributes SET {column_name} = ? WHERE rowid = ?", (value, rowid))
                    logger.info('Parameters has been pushed to the Attributes table successfully')
                else:
                    # If there are no more NULL rows, insert a new row
                    self.cursor.execute(f"INSERT INTO Attributes DEFAULT VALUES")
                    rowid = self.cursor.lastrowid
                    self.cursor.execute(f"UPDATE Attributes SET {column_name} = ? WHERE rowid = ?", (value, rowid))
            logger.info('Parameters has been pushed to the Attributes table successfully')
            self.connection.commit()
            self.close()
            return "Data inserted successfully"
            
        
        except sqlite3.Error as e:
            print(f"Error inserting attributes for column: {column_name} - {e}")
            logging.warning('Error, recheck the values you are trying to insert')
            self.close()
            return "Error inserting attributes"

    def get_attributes(self, column_name):
        try:
            self.cursor.execute(f"SELECT {column_name} FROM Attributes WHERE {column_name} IS NOT NULL")
            result = self.cursor.fetchall()
            if result:
                attributes = [row[0] for row in result]
                logger.info('Attrbiutes has been found')
                self.close()
                return attributes
            else:
                print(f"No attributes found for column: {column_name}")
                self.close()
                return None
        except sqlite3.Error as e:
            print(f"Error fetching attributes for column: {column_name} - {e}")
            logging.error('Error, attributes cannot be found')
            self.close()
            return None

    def read_table(self, table_name):
        """
        Reads all the information from the specified table in the 'testDB.db' database.

        Args:
        table_name (str): Name of the table to read data from.

        Returns:
        pandas.DataFrame: A DataFrame containing all the data from the table.
        """
        # Read the table into a pandas DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connection)
        logger.info('Table has been shown')
        self.close()
        return df


    def insert_rows(self, table_name, df):
        """
        Inserts rows into the specified table.

        Args:
        table_name (str): Name of the table to insert rows into.
        df (DataFrame): Pandas DataFrame containing rows to insert.

        Returns:
        str: A message indicating the success or failure of the operation.
        """
        try:
            # Get the number of columns in the table
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            table_columns = [row[1] for row in self.cursor.fetchall()]
            print("Table Columns:", table_columns)  # Add this line
            
            # Check if the number of columns in the DataFrame matches the number of columns in the table
            print("DataFrame Columns:", df.columns)  # Add this line
            if len(df.columns) != len(table_columns):
                self.close()
                logger.error(f"Number of columns in DataFrame ({len(df.columns)}) doesn't match the number of columns in the table ({len(table_columns)}).")
                return f"Number of columns in DataFrame ({len(df.columns)}) doesn't match the number of columns in the table ({len(table_columns)})."

            # Convert all values in the DataFrame to strings
            df = df.applymap(str)

            # Check for non-convertible values
            for column in df.columns:
                if not df[column].apply(lambda x: isinstance(x, str)).all():
                    logger.error("Non-convertible values found in column")
                    return f"Non-convertible values found in column '{column}'."

            # Insert data into the specified table
            self.cursor.executemany(f"INSERT INTO {table_name} VALUES ({','.join(['?' for _ in range(len(table_columns))])})", df.values.tolist())
            logger.info("Rows were inserted successfully!")
            self.connection.commit()
            self.close()
            
            return "Rows inserted successfully."
        except sqlite3.Error as e:
            logger.error("You have error when inserting rows into table")
            self.close()
            return f"Error inserting rows into table {table_name}: {e}"

    def remove_column_or_row(self, column_name, to_remove):
        try:
            # Check if column exists in the table schema
            self.cursor.execute(f"PRAGMA table_info(Attributes)")
            columns = [row[1] for row in self.cursor.fetchall()]

            # Check if 'column_name' exists in the table
            if column_name not in columns:
                print(f"Column '{column_name}' does not exist in the table.")
                logger.warning('The columns you are trying to remove doesnt exist in the table')
                self.close()
                return

            # Check if 'to_remove' is a valid value
            if to_remove in columns:
                # Remove the entire column specified by 'to_remove'
                self.cursor.execute(f"ALTER TABLE Attributes DROP COLUMN {to_remove}")
                print(f"Column '{to_remove}' removed successfully.")
                logger.info("The column(s) where removed")
                self.close()
            else:
                # Remove the entire row where the specified value is located
                self.cursor.execute(f"DELETE FROM Attributes WHERE {column_name} = ?", (to_remove,))
                print(f"Row with value '{to_remove}' from column '{column_name}' removed successfully.")
                logger("The operation has been completed successfully")
                self.close()

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error removing '{to_remove}': {e}")
            logger.error('Error while trying to remove the specifed column/row')
            self.close()


    def get_row_from_survey(self, table_name, index):
        """
        Retrieves a row from the specified table based on its basic index.

        Args:
        table_name (str): Name of the table to retrieve the row from.
        index (int): The index of the row to retrieve (0-based).

        Returns:
        tuple: A tuple containing the values of the row retrieved.
        """
        try:
            # Execute query to fetch the row based on index
            self.cursor.execute(f"SELECT * FROM {table_name} LIMIT 1 OFFSET ?", (index,))
            row = self.cursor.fetchone()
            if row:
                logger.info('The operation completed successfully')
                self.close()
                return row  # Return tuple containing row values
            else:
                print(f"No row found at index {index} in table {table_name}")
                logger.warning('the specified row is not found at the exact index')
                self.close()
                return None
        except sqlite3.Error as e:
            print(f"Error fetching row from table {table_name}: {e}")
            logger.error("Errow while trying get a row")
            self.close()
            return None

    def store_response(self, Respondent_ID, Attributes, Best_Attribute, Worst_Attribute, Block, Task, Age_Range, Gender):
        try:
            for Attribute in Attributes:
                Response = 0
                if Attribute == Best_Attribute:
                    Response = 1
                elif Attribute == Worst_Attribute:
                    Response = -1

                insert_query = "INSERT INTO response_Apple__Iphone (Respondent_ID, Attribute, Block, Task, Response, Age_Range, Gender) VALUES (?, ?, ?, ?, ?, ?, ?)"
                self.cursor.execute(insert_query, (Respondent_ID, Attribute, Block, Task, Response, Age_Range, Gender))

            self.connection.commit()
            logger.info('Operated completed successfully')
            self.close()
        except Exception as e:
            self.close()
            self.connection.rollback()
            raise e

    def create_response_iphone_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS response_Apple__Iphone (
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
        self.cursor.execute(create_table_query)
        self.connection.commit()
        logger.info('Table created successfully')
        self.close()

    def sql_to_pandas(self, query):
        df = pd.read_sql_query(query, self.connection)
        self.close()
        return df

    def pandas_to_sql(self, df, table_name, if_exists='replace'):
        df.to_sql(table_name, self.connection, if_exists=if_exists, index=False)
        self.close()
