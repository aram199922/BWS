import os
import sys
import sqlite3
import pandas as pd
import logging
from ..logger import *
from BWS.api.main import app

# current_directory = os.getcwd()
# sys.path.insert(0, current_directory)


logger = logging.getLogger(os.path.basename(__file__))
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)


class SqlHandle:
    """
    Class with all the methods for interacting with the database

    """    
    def __init__(self, db_name="testDB.db"):
        """Creating the instance of db connection

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()

        Args:
            db_name (str, optional): _description_. Defaults to "testDB.db".
        """        
        self.db_name = db_name
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()

    def close(self):
        """Function which will close the connection

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.close()
        """        
        self.connection.close()
        logger.info('the connection has been closed')

    def create_database(self):
        """Function for creating the db

        """        
        if not os.path.exists(self.db_name):
            logger.info('Database has been created')
            print("Database created successfully.")
            logger.info('Database has been created')
        else:
            print("Database already exists.")
            logger.warning('You are trying to create a database that already exists')


    def push_flat_file_to_database(self, file_name, table_name:str):
        """Function for pushing flat files to the database

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.push_flat_file_to_database('master_design.csv', 'Master_Design')
        
        Args:
            file_name (_type_): name of the file
            table_name (str): name of the table that is going to be created
        """        
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
    

    def insert_attributes(self, column_name:str, values_list:list)->str:
        """Function for inserting the attributes

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.insert_attributes('Dell_Notebook', ['Screen','Ram','VideoCard'])

        Args:
            column_name (str): name of company product
            values_list (list): list of attributes

        Returns:
            str: clarification
        """          
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
            return "Data inserted successfully"
            
        
        except sqlite3.Error as e:
            print(f"Error inserting attributes for column: {column_name} - {e}")
            logging.warning('Error, recheck the values you are trying to insert')
            return "Error inserting attributes"

    def get_attributes(self, column_name:str)->list:
        """Getting the desired attribute list

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.get_attributes('Dell_Notebook')

        Args:
            column_name (str): name of the column

        Returns:
            list: list of the column values
        """        
        try:
            self.cursor.execute(f"SELECT {column_name} FROM Attributes WHERE {column_name} IS NOT NULL")
            result = self.cursor.fetchall()
            if result:
                attributes = [row[0] for row in result]
                logger.info('Attributes have been found')
                return attributes
            else:
                print(f"No attributes found for column: {column_name}")
                return None
        except sqlite3.Error as e:
            print(f"Error fetching attributes for column: {column_name} - {e}")
            logging.error('Error, attributes cannot be found')
            return None

    def read_table(self, table_name:str)->pd.DataFrame:
        """Return the table in dataframe format

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.read_table('Master_Design')

        Args:
            table_name (str): name of the table

        Returns:
            pd.DataFrame: dataframe of the table
        """
        # Read the table into a pandas DataFrame
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", self.connection)
        logger.info('Table has been shown')
        return df


    def insert_rows(self, table_name:str, df:pd.DataFrame)->str:
        """Inserting rows into the table

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.insert_rows('Response_Dell_Notebook', responses)

        Args:
            table_name (str): Name of the table
            df (pd.DataFrame): dataframe which rows are going to be inserted

        Returns:
            str: clarification
        """    
        try:
            # Get the number of columns in the table
            self.cursor.execute(f"PRAGMA table_info({table_name})")
            table_columns = [row[1] for row in self.cursor.fetchall()]
            print("Table Columns:", table_columns)  # Add this line
            
            # Check if the number of columns in the DataFrame matches the number of columns in the table
            print("DataFrame Columns:", df.columns)  # Add this line
            if len(df.columns) != len(table_columns):
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
            
            return "Rows inserted successfully."
        except sqlite3.Error as e:
            logger.error("You have error when inserting rows into table")
            return f"Error inserting rows into table {table_name}: {e}"

    def remove_column_or_row(self, column_name:str, to_remove:str):
        """Removing column or row from table Attributes
        If the same values will delete column else only the value of the column

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.remove_column_or_row('Dell_Notebook', 'Screen')
            >>> inst.remove_column_or_row('Dell_Notebook', 'Dell_Notebook')

        Args:
            column_name (str): name of the column
            to_remove (str): remove whole column or value in it
        """        
        try:
            # Check if column exists in the table schema
            self.cursor.execute(f"PRAGMA table_info(Attributes)")
            columns = [row[1] for row in self.cursor.fetchall()]

            # Check if 'column_name' exists in the table
            if column_name not in columns:
                print(f"Column '{column_name}' does not exist in the table.")
                logger.warning('The columns you are trying to remove doesnt exist in the table')
                return

            # Check if 'to_remove' is a valid value
            if to_remove in columns:
                # Remove the entire column specified by 'to_remove'
                self.cursor.execute(f"ALTER TABLE Attributes DROP COLUMN {to_remove}")
                print(f"Column '{to_remove}' removed successfully.")
                logger.info("The column(s) where removed")
            else:
                # Remove the entire row where the specified value is located
                self.cursor.execute(f"DELETE FROM Attributes WHERE {column_name} = ?", (to_remove,))
                print(f"Row with value '{to_remove}' from column '{column_name}' removed successfully.")
                logger("The operation has been completed successfully")

            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Error removing '{to_remove}': {e}")
            logger.error('Error while trying to remove the specifed column/row')
    

    def get_row_from_survey(self, table_name:str, index:int, block:int)->tuple:
        """Getting row (question) from the survey

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.get_row_from_survey('Response_Dell_Notebook', 1, 2)

        Args:
            table_name (str): name of the survey table
            index (int): index of row to get
            block (int): from which block of questions to get

        Returns:
            tuple: tuple containing row values
        """
        try:
        # Execute query to fetch the row based on index and block
            self.cursor.execute(f"SELECT * FROM {table_name} WHERE block = ? LIMIT 1 OFFSET ?", (block, index,))
            row = self.cursor.fetchone()
            if row:
                logger.info("The row from survey has imported successfully")
                return row  # Return tuple containing row values
            else:
                print(f"No row found at index {index} and block {block} in table {table_name}")
                logger.warning("Row is not found")
                return None
        except sqlite3.Error as e:
            print(f"Error fetching row from table {table_name}: {e}")
            logger.error("Error, make sure you filled everything correctly")
            return None

    def store_response(self, table_name:str, Respondent_ID:int, Attributes:list, Best_Attribute:str, Worst_Attribute:str, Block:int, Task:int, Age_Range:str, Gender:str):
        """Function for storing the answer of the user in the table

        Args:
            table_name (str): Name of the table
            Respondent_ID (int): Id of the respondent
            Attributes (list): Attribute list of the product
            Best_Attribute (str): Chosen best
            Worst_Attribute (str): Chosen worst
            Block (int): Block number
            Task (int): Task number
            Age_Range (str): Age range of the user
            Gender (str): Gender of the user

        Raises:
            e: Error
        """
        try:
            for Attribute in Attributes:
                Response = 0
                if Attribute == Best_Attribute:
                    Response = 1
                    logger.info("The best Attribute is stored")
                elif Attribute == Worst_Attribute:
                    Response = -1
                    logger.info("The worst Attribute is stored")

                # Construct the INSERT query with the provided column name and table name
                insert_query = f"INSERT INTO {table_name} (Response, Attribute, Respondent_ID, Block, Task, Age_Range, Gender) VALUES (?, ?, ?, ?, ?, ?, ?)"
                self.cursor.execute(insert_query, (Response, Attribute, Respondent_ID, Block, Task, Age_Range, Gender))

            self.connection.commit()
            logger.info('Operation completed successfully')
        except Exception as e:
            self.connection.rollback()
            logger.warning("Make sure you filled everything correctly")
            raise e

        

    def create_response_table(self, table_name:str):
        """Creating table for responses of the specific product if does not exist

        Args:
            table_name (str): Name of the table
        """              
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
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

    def update_product_name(self, company: str, old_product: str, new_product: str):
        """This function give the opportunity to change product name.

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.update_product_name('Dell', 'Notebook', 'Headphones')

        Args:
            company (str): Name of the company
            old_product (str): Name of the old product
            new_product (str): Name of new product to which will be updated

        Returns:
            _type_: Clarification
        """        
        try:
            # Construct the column name based on the provided company and product
            column_name = f"{company}__{old_product}"
        
            # Check if the column exists in the Attributes table
            self.cursor.execute("PRAGMA table_info(Attributes)")
            columns = [row[1] for row in self.cursor.fetchall()]
            if column_name not in columns:
                logger.warning('The specifed column does not exist')
                return f"Column '{column_name}' does not exist."

        # Construct the SQL query to update the column name to the new product name
            query = f"ALTER TABLE Attributes RENAME COLUMN {column_name} TO {company}__{new_product}"
        
        # Execute the SQL query to update the column name
            self.cursor.execute(query)
            self.connection.commit()
            logger.info("Product name updated successfully")
            return f"Product name updated successfully from '{old_product}' to '{new_product}'."
        except sqlite3.Error as e:
            self.connection.rollback()
            logger.error('Error make sure you filled everything correctly')
            return f"Error updating product name: {e}"
        
    def is_table_empty(self, table_name:str)->bool:
        """Checks if the following table is empty or not

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.is_table_empty('response_Dell_Notebook')

        Args:
            table_name (str): Name of the table

        Returns:
            bool: Boolean if empty or not
        """                
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            logger.info('The information about the table recieved successfully')
            return count == 0
        except sqlite3.Error as e:
            print(f"Error checking if table '{table_name}' is empty: {e}")
            return False

    def get_last_respondent_ID(self, table_name:str):
        """Checks the number of respondents ID-s assuming 1 incremention during surveying process

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.get_last_respondent_ID('response_Dell_Notebook')

        Args:
            table_name (str): Name of the table

        Returns:
            int: Last Respondent's ID as int
        """        
        try:
            self.cursor.execute(f"SELECT MAX(Respondent_ID) FROM {table_name}")
            last_respondent_ID = self.cursor.fetchone()[0]
            logger.info("The operation completed successfully")
            return last_respondent_ID
        except sqlite3.Error as e:
            print(f"Error fetching last Respondent ID from table '{table_name}': {e}")
            logger.error("Error recheck the inserted data")
            return None


    def sql_to_pandas(self, query:str)->pd.DataFrame:
        """Reads the table into pandas dataframe

        Args:
            query (str): query to be executed 

        Returns:
            pd.DataFrame: the dataframe of table
        """            
        df = pd.read_sql_query(query, self.connection)
        logger.info('SQL To Pandas')
        return df

    def pandas_to_sql(self, df:pd.DataFrame, table_name:str, if_exists='replace'):
        """Function that gives the opportunity to push dataframe into the DataBase

        Examples:
            >>> from BWS.database.db_interactions import SqlHandle
            >>> inst = SqlHandle()
            >>> inst.pandas_to_sql(df_analysis_dell_notebook, 'analysis_Dell_Notebook')

        Args:
            df (pd.DataFrame): _description_
            table_name (str): _description_
            if_exists (str, optional): If the table exists then updates. Defaults to 'replace'.
        """        
        df.to_sql(table_name, self.connection, if_exists=if_exists, index=False)
        logger.info("Pandas To SQL")
