from .main import app
from ..database.db_interactions import SqlHandle

inst = SqlHandle()

# Getting company and product name and product's attributes
@app.post("/Provide Company Details/{Company}&{Product}")
async def inserting_attributes(Company: str, Product: str, Attributes: list[str]):
    """
    Please provide your company's name, product and its attributes.

    Example of attributes format: ["Attribute1", "Attribute2", "Attribute3"]

    Args:
        Company (str): Name of the company
        Product (str): Name of the product
        Attributes (list[str]): List of attributes characterizing the product

    Returns:
        str: Clarification
    """
    column_name = f"{Company}__{Product}"
    inst.insert_attributes(column_name, Attributes)
    return {"Data inserted successfully"}
    #return {'product': column_name, 'attributes': Attributes}