from fastapi import FastAPI
from BWS.database.db_interactions import SqlHandle

app = FastAPI()

@app.get("/analysis")
def get_product_analysis(company_name: str, product_name: str):
    sql_handler = SqlHandle()  # Assuming this initializes your database connection
    table_names = [f"analysis{i}_{company_name}__{product_name}" for i in range(1, 4)]
    results = {}

    for table_name in table_names:
        try:
            df = sql_handler.read_table(table_name)
            if df is not None:
                results[table_name] = df.to_dict(orient="records")
            else:
                results[table_name] = None
        except Exception as e:
            results[table_name] = str(e)

    return results
