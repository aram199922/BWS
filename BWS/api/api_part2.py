import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from fastapi import FastAPI, HTTPException, Query
from BWS.database.db_interactions import get_row_from_survey
from BWS.database.db_interactions import create_response_iphone_table
from BWS.database.db_interactions import store_response

app = FastAPI()

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


# Function to set and retrieve the respondent's age range
def get_age_range():
    if "age_range" not in respondent_info:
        raise HTTPException(status_code=400, detail="Age range not provided")
    return respondent_info["age_range"]


@app.post("/user/id", response_model=dict)
async def store_user_id(user_id: int = Query(..., description="Please type an ID")):
    """
    Store a unique id for each user.
    """
    # Store the user id in the respondent_info dictionary
    respondent_info["user"] = user_id

    return {"message": "User ID saved successfully"}

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


from typing import List

@app.get("/block/tasks", response_model=dict)
async def get_current_task():
    """
    Retrieve attributes for the current task and allow users to select best and worst attributes.
    """
    global current_task

    if current_task > 10:
        return {"message": "Thank you for your feedback!"}

    # Retrieve attributes for the current task from the survey table
    row = get_row_from_survey("survey_Apple__Iphone", current_task - 1)  # Index is 0-based
    if not row:
        raise HTTPException(status_code=404, detail=f"No attributes found for Task {current_task}")

    # Extract attributes from the row
    attributes = row[2:]

    # Prepare response with task ID and attributes
    response = {
        "task_id": current_task,
        "attributes": {attribute for i, attribute in enumerate(attributes)}
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
    row = get_row_from_survey("survey_Apple__Iphone", task_id - 1)  # Index is 0-based
    if not row:
        raise HTTPException(status_code=404, detail=f"No attributes found for Task {task_id}")
    
    # Extract attributes from the row
    available_attributes = row[2:]

    # Check if the selected attributes are available for the task
    if best_attribute not in available_attributes or worst_attribute not in available_attributes:
        raise HTTPException(status_code=400, detail=f"Invalid attribute selection. Task {task_id} does not have the selected attribute(s)")

    # Create table if it does not exist
    create_response_iphone_table()
    
    # Store the selected best and worst attributes, along with user_id, age range, gender in the database
    try:
        store_response(user=respondent_info.get("user"), block=1, task=task_id, attributes=available_attributes, best_attribute=best_attribute, worst_attribute=worst_attribute, age_range=age_range, gender=gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store attribute response")

    return {"task_id": task_id, "best_attribute": best_attribute, "worst_attribute": worst_attribute}