import uvicorn
from starlette.responses import RedirectResponse
from BWS.database.db_interactions import SqlHandle

from BWS.api.api_part3 import app

Inst2 = SqlHandle()
Inst2.create_database()

# Redirect root URL to /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8003)