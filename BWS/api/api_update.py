import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from BWS.api.main import app
from fastapi import HTTPException


import sqlite3


def update_product_name(company: str, old_product: str, new_product: str):
    db = sqlite3.connect("testDB.db")  
    cursor = db.cursor()
    try:
        # Construct the column name based on the provided company and product
        column_name = f"{company}__{old_product}"
        
        # Check if the column exists in the Attributes table
        cursor.execute(f"PRAGMA table_info(Attributes)")
        columns = [row[1] for row in cursor.fetchall()]
        if column_name not in columns:
            db.close()
            return f"Column '{column_name}' does not exist."

        # Construct the SQL query to update the column name to the new product name
        query = f"ALTER TABLE Attributes RENAME COLUMN {column_name} TO {company}__{new_product}"
        
        # Execute the SQL query to update the column name
        cursor.execute(query)
        db.commit()
        db.close()
        return f"Product name updated successfully from '{old_product}' to '{new_product}'."
    except sqlite3.Error as e:
        db.rollback()
        db.close()
        return f"Error updating product name: {e}"

@app.put("/update_product_name/{company}/{old_product}")
async def update_product(company: str, old_product: str, new_product: str):
    """
    Endpoint to update the product name in the Attributes table.
    """
    # Call the function to update the product name
    result = update_product_name(company, old_product, new_product)
    if "successfully" in result.lower():
        return {"message": result}
    else:
        raise HTTPException(status_code=404, detail=result)