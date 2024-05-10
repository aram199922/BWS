import os
import sys

#current_directory = os.getcwd()
#sys.path.insert(0, current_directory)

from BWS.api.main import app
from BWS.database.db_interactions import SqlHandle

inst = SqlHandle()

# Getting company and product name and product's attributes
@app.post("/Provide Company Details/")
async def inserting_attributes(Company: str, Product: str, Attributes: list[str]):
    """
    Please provide your company's name, product and its attributes.

    Example of attributes format: ["Attribute1", "Attribute2", "Attribute3"]
    """
    column_name = f"{Company}__{Product}"
    inst.insert_attributes(column_name, Attributes)
    return {"Data inserted successfully"}