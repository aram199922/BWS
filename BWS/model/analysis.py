import numpy as np
import pandas as pd
from .. import utils
from ..database import db_interactions

def get_survey_design(column_name):
    """
    Retrieve the specified column from the database and create the design.

    Parameters:
    - column_name: The name of the column to retrieve.

    Returns:
    - survey_design: A dataframe of the specfic product survey design.
    """
    # Assuming the column name is already sanitized
    column_data = db_interactions.get_attributes(column_name)

    if column_data:
        # Extract values from tuples and handle NaN values
        column_values = column_data
    else:
        print("No attributes found for the specified column.")
        column_values = []
        return
    # Pass the column values to the design_creation function
    if column_values:
        survey_design = utils.design_creation(column_values)
    else:
        print("No attributes found for the specified column.")
        # Handle the case where no attributes are found for the specified column
        return

    return survey_design

def push_survey_design(column_name,survey_design):
    table_name = f"survey_{column_name}"
    db_interactions.pandas_to_sql(survey_design, table_name)
    return

def push_analysis1(product_name): 
    data = db_interactions.read_table(f"response_{product_name}") 
    data.drop(columns=['id'], inplace=True) 
    result = utils.output_1_simple_demographic(data) 
    db_interactions.pandas_to_sql(result, f"analysis1_{product_name}") 
    return

def push_analysis2(product_name): 
    data = db_interactions.read_table(f"response_{product_name}") 
    data.drop(columns=['id'], inplace=True) 
    result = utils.output_2_general_importance_plot_df(data) 
    db_interactions.pandas_to_sql(result, f"analysis2_{product_name}") 
 
def push_analysis3(product_name): 
    data = db_interactions.read_table(f"response_{product_name}") 
    data.drop(columns=['id'], inplace=True) 
    result = utils.output_3_4_importance_by_demographic(data) 
    db_interactions.pandas_to_sql(result, f"analysis3_{product_name}")