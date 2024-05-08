import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from fastapi import FastAPI, HTTPException, Query
from BWS.api.response import get_row_from_survey
from BWS.api.response import create_response_phone
from BWS.api.response import store_response

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


@app.post("/Respondent_ID", response_model=dict)
async def store_respondent_id(Respondent_ID: int = Query(..., description="Please type an ID")):
    """
    Store a unique Responent ID for each user.
    """
    # Store the user id in the respondent_info dictionary
    respondent_info["user"] = Respondent_ID

    return {"message": "Respondent ID saved successfully"}

@app.post("/Demographics/Age_Range", response_model=dict)
async def select_age_range(Age_Range: str = Query(..., description="Please select your age range from the options provided above")):
    """
    Please select your age range:
    - Under 18: <18,
    - 18-25: 18-25,
    - 26-35: 26-35,
    - 36-45: 36-45,
    - Above 45: >45
    """
    if Age_Range not in age_ranges.values():
        raise HTTPException(status_code=400, detail="Invalid age range selected")

    # Store respondent's age range
    respondent_info["age_range"] = Age_Range

    return {"message": "Age range saved successfully"}

@app.post("/demographics/gender", response_model=dict)
async def select_gender(Gender: str = Query(..., description="Please select your gender")):
    """
    Gender:
    - Female
    - Male
    """
    if Gender.lower() not in gender_options:
        raise HTTPException(status_code=400, detail="Invalid gender selected")

    # Store respondent's gender
    respondent_info["gender"] = Gender.lower()

    return {"message": "Gender saved successfully"}

last_task_id = None

@app.get("/block/tasks", response_model=dict)
async def get_current_task(Respondent_ID: int = Query(..., description="Please provide your user ID")):
    """
    Retrieve attributes for the current task and allow users to select best and worst attributes.
    """
    global current_task, last_task_id

    if current_task > 10:
        return {"message": "Thank you for your feedback!"}

    # Determine the block for the user based on their ID
    block = ((Respondent_ID - 1) % 10) + 1

    # Retrieve attributes for the current task from the survey table based on the block
    row = get_row_from_survey("survey_Apple__Iphone", current_task - 1, block)  # Index is 0-based
    if not row:
        raise HTTPException(status_code=404, detail=f"No attributes found for Task {current_task} and Block {block}")

    # Extract attributes from the row
    attributes = row[2:]

    # Prepare response with task ID and attributes
    response = {
        "task_id": current_task,
        "attributes": attributes
    }

    # Store the current task ID as the last task ID
    last_task_id = current_task

    # Automatically move to the next task for the next request
    current_task += 1

    return response



@app.post("/block/tasks/selection", response_model=dict)
async def select_task_attributes(best_attribute: str = Query(None), worst_attribute: str = Query(None)):
    """
    Allow users to select best and worst attributes for the current task.
    """
    global last_task_id

    Respondent_ID = respondent_info.get("user")
    if not Respondent_ID:
        raise HTTPException(status_code=400, detail="User ID not provided")
    
    # Calculate block based on user ID
    block = ((Respondent_ID - 1) % 10) + 1
    
    Age_Range = get_age_range()
    Gender = respondent_info.get("gender")

    # Check if last_task_id is None, indicating that no GET request has been made yet
    if last_task_id is None:
        raise HTTPException(status_code=400, detail="No task selected. Please retrieve a task using the GET endpoint first.")

    # Retrieve attributes for the specified task from the survey table
    row = get_row_from_survey("survey_Apple__Iphone", last_task_id - 1, block)  # Index is 0-based
    if not row:
        raise HTTPException(status_code=404, detail=f"No attributes found for Task {last_task_id}")
    
    # Extract attributes from the row
    available_attributes = row[2:]

    # Check if the selected attributes are available for the task
    if best_attribute not in available_attributes or worst_attribute not in available_attributes:
        raise HTTPException(status_code=400, detail=f"Invalid attribute selection. Task {last_task_id} does not have the selected attribute(s)")

    # Create table if it does not exist
    create_response_phone()
    
    # Store the selected best and worst attributes, along with Respondent_ID, age range, gender, and block in the database
    try:
        store_response(Respondent_ID=Respondent_ID, Block=block, Task=last_task_id, Attributes=available_attributes, Best_Attribute=best_attribute, Worst_Attribute=worst_attribute, Age_Range=Age_Range, Gender=Gender)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to store attribute response")

    return {"best_attribute": best_attribute, "worst_attribute": worst_attribute}