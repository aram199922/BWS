import os
import sys
import sqlite3
from BWS.api.main import app
from fastapi import HTTPException
from BWS.database import SqlHandle


#current_directory = os.getcwd()
#sys.path.insert(0, current_directory)

instance = SqlHandle


@app.put("/update_product_name/{company}/{old_product}")
async def update_product(company: str, old_product: str, new_product: str):
    """
    Endpoint to update the product name in the Attributes table.
    """
    # Call the function to update the product name
    result = instance.update_product_name(company, old_product, new_product)
    if "successfully" in result.lower():
        return {"message": result}
    else:
        raise HTTPException(status_code=404, detail=result)