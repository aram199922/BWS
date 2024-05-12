from .main import app
from ..database.db_interactions import SqlHandle
from fastapi import HTTPException

instance = SqlHandle()

@app.put("/update_product_name/{company}/{old_product}")
async def update_product(company: str, old_product: str, new_product: str):
    """
    Endpoint to update the product name in the Attributes table.

    Args:
        company (str): Company Name
        old_product (str): Old Product Name
        new_product (str): New Product Name

    Raises:
        HTTPException: _description_

    Returns:
        dict: Message of the updata
    """
    # Call the function to update the product name
    result = instance.update_product_name(company, old_product, new_product)
    if "successfully" in result.lower():
        return {"message": result}
    else:
        raise HTTPException(status_code=404, detail=result)