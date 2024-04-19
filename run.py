import uvicorn
import os
from BWS.api import app

if __name__=="__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)