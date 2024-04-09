import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse
from BWS.database.db_interactions import insert_attributes

app = FastAPI()

@app.post("/Provide your company name, product and its attributes/")
async def inserting_attributes(Company: str, Product: str, Attributes: list[str]):
    column_name = f"{Company} {Product}"
    insert_attributes(column_name, Attributes)
    return {"Data inserted successfully"}

# Redirect root URL to /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
