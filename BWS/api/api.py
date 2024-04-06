from fastapi import FastAPI
from typing import List
import sqlite3

app = FastAPI()


#Code to get the company name, product name and attributes
#I ran this by python -m uvicorn api:app
def insert_attributes(table_name, column_name, attribute_list):
    conn = sqlite3.connect('testDB.db')
    c = conn.cursor()
    c.execute(f"INSERT INTO {table_name} (column_name, attribute_list) VALUES (?, ?)", (column_name, attribute_list))
    conn.commit()
    conn.close()

@app.post("/create_product")
async def create_product(company: str, product: str, attributes: str):
    column_name = f"{company}.{product}"
    # Split the attributes string into a list using comma as delimiter
    attributes_list = attributes.split(",")
    insert_attributes("products", column_name, ",".join(attributes_list))
    return {"message": "Product created successfully"}
