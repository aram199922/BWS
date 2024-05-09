import uvicorn
from starlette.responses import RedirectResponse
from BWS.database.db_interactions import SqlHandle

# Run this file
# from BWS.api import app

# Comment the previous line, uncomment the next line and run
# from BWS.api.api_part2 import app

# Comment the previous line, uncomment the next line and run
# from BWS.api.api_update import app

from BWS.api.part2_test import app
Inst2 = SqlHandle()
print(Inst2.create_database())
Inst2.close()


# Redirect root URL to /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)