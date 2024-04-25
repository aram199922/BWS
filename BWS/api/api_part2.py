import os
import sys
import sqlite3

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from fastapi import FastAPI, HTTPException, Query
from starlette.responses import RedirectResponse
from typing import Dict
from BWS.database.db_interactions import get_row_from_survey


app = FastAPI()

def create_task_attributes_table():
    conn = sqlite3.connect("testDB.db")  # Connecting to SQLite database
    cursor = conn.cursor()

    create_table_query = """
    CREATE TABLE IF NOT EXISTS task_attributes (
        id INTEGER PRIMARY KEY,
        block INTEGER,
        task INTEGER,
        attribute TEXT,
        response INTEGER,
        age_range TEXT,
        gender TEXT,
        user INTEGER  -- New column for storing unique user numbers
    )
    """
    cursor.execute(create_table_query)
    conn.commit()
    conn.close()

def store_task_attributes(block, task, attributes, best_attribute, worst_attribute, age_range, gender, user):
    conn = sqlite3.connect("testDB.db")  # Connecting to SQLite database
    cursor = conn.cursor()

    try:
        for attribute in attributes:
            response = 0  # Default response
            if attribute == best_attribute:
                response = 1
            elif attribute == worst_attribute:
                response = -1

            insert_query = "INSERT INTO task_attributes (block, task, attribute, response, age_range, gender, user) VALUES (?, ?, ?, ?, ?, ?, ?)"
            cursor.execute(insert_query, (block, task, attribute, response, age_range, gender, user))

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()



current_task = 1  # Initialize current task to 1

# Define age ranges for demographic questions
age_ranges = {
    "Under 18": "<18",
    "18-25": "18-25",
    "26-35": "26-35",
    "36-45": "36-45",
    "Above 45": ">45"
}

# Define gender options
gender_options = ["female", "male"]

# Store respondent's demographic information
respondent_info = {}

from fastapi import Depends

# Function to set and retrieve the respondent's age range
def get_age_range():
    if "age_range" not in respondent_info:
        raise HTTPException(status_code=400, detail="Age range not provided")
    return respondent_info["age_range"]


@app.post("/user/number", response_model=dict)
async def store_user_number(user_number: int = Query(..., description="Please provide your unique user number")):
    """
    Store a unique number for each user.
    """
    # Store the user number in the respondent_info dictionary
    respondent_info["user"] = user_number

    return {"message": "User number saved successfully"}

@app.post("/demographics/age_range", response_model=dict)
async def select_age_range(age_range: str = Query(..., description="Please select your age range from the options provided above")):
    """
    Please select your age range:
    - Under 18: <18,
    - 18-25: 18-25,
    - 26-35: 26-35,
    - 36-45: 36-45,
    - Above 45: >45
    """
    if age_range not in age_ranges.values():
        raise HTTPException(status_code=400, detail="Invalid age range selected")

    # Store respondent's age range
    respondent_info["age_range"] = age_range

    return {"message": "Age range saved successfully"}

@app.post("/demographics/gender", response_model=dict)
async def select_gender(gender: str = Query(..., description="Please select your gender")):
    """
    Gender:
    - Female
    - Male
    """
    if gender.lower() not in gender_options:
        raise HTTPException(status_code=400, detail="Invalid gender selected")

    # Store respondent's gender
    respondent_info["gender"] = gender.lower()

    return {"message": "Gender saved successfully"}


@app.get("/block/tasks", response_model=dict)
async def get_current_task():
    """
    Retrieve attributes for the current task and allow users to select best and worst attributes.
    """
    global current_task

    # Retrieve attributes for the current task from the survey table
    row = get_row_from_survey("survey_lyov", current_task - 1)  # Index is 0-based
    if not row:
        raise HTTPException(status_code=404, detail=f"No attributes found for Task {current_task}")

    # Extract attributes from the row
    attributes = row[2:]

    # Construct the list of attributes with options for the user
    attribute_options = {f"Attribute {i+1}": attribute for i, attribute in enumerate(attributes)}

    # Prepare response with task ID, attributes, and attribute options
    response = {
        "task_id": current_task,
        "attributes": attributes,
        "attribute_options": attribute_options
    }

    # Automatically move to the next task for the next request
    current_task += 1

    return response


@app.post("/block/tasks/{task_id}/selection", response_model=dict)
async def select_task_attributes(task_id: int, best_attribute: str = Query(None), worst_attribute: str = Query(None)):
    """
    Allow users to select best and worst attributes for the current task.
    """
    age_range = get_age_range()
    gender = respondent_info.get("gender")

    # Check if task_id matches the expected current task
    if task_id != current_task - 1:
        raise HTTPException(status_code=400, detail=f"Invalid task ID. Expected: {current_task - 1}")
    
    # Retrieve attributes for the specified task from the survey table
    row = get_row_from_survey("survey_lyov", task_id - 1)  # Index is 0-based
    if not row:
        raise HTTPException(status_code=404, detail=f"No attributes found for Task {task_id}")
    
    # Extract attributes from the row
    available_attributes = row[2:]

    # Check if the selected attributes are available for the task
    if best_attribute not in available_attributes or worst_attribute not in available_attributes:
        raise HTTPException(status_code=400, detail=f"Invalid attribute selection. Task {task_id} does not have the selected attribute(s)")

    # Create table if does not exist
    create_task_attributes_table()

    # Store the selected best and worst attributes, along with age range, in the database
    try:
        store_task_attributes(block=1, task=task_id, attributes=available_attributes, best_attribute=best_attribute, worst_attribute=worst_attribute, age_range=age_range, gender=gender, user=respondent_info.get("user"))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store attribute response")

    return {"task_id": task_id, "best_attribute": best_attribute, "worst_attribute": worst_attribute}


# Redirect root URL to /docs
@app.get("/", include_in_schema=False)
async def redirect_to_docs():
    return RedirectResponse(url="/docs")


import uvicorn
import os


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)