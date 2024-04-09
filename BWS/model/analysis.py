from __init__ import design_creation
from ..database.Function_Codes import get_attributes

def get_survey_design(column_name):
    """
    Retrieve the specified column from the database.

    Parameters:
    - column_name: The name of the column to retrieve.

    Returns:
    - column_data: A list containing the values of the specified column.
    """
    # Assuming the column name is already sanitized
    column_data = get_attributes(column_name)

    if column_data:
        # Extract values from tuples and handle NaN values
        column_values = [value[0] for value in column_data if value[0] is not None]
    else:
        print("No attributes found for the specified column.")
        column_values = []
        return
    # Pass the column values to the design_creation function
    if column_values:
        survey_design, numbered_design = design_creation(column_values)
    else:
        print("No attributes found for the specified column.")
        # Handle the case where no attributes are found for the specified column
        return

    return survey_design

def push_survey_design(survey_design, column_name):
    table_name = f"survey.{column_name}"
    pandas_to_sql(survey_design, table_name)
    return

column_name = "xiomi"

