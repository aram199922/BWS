import sqlite3
import random
from BWS.database.db_interactions import create_response_iphone_table

''' 
    This file is for inserting values to response_Apple__Iphone table to conduct analysis on that.
'''


# Connect to the database
db = sqlite3.connect('testDB.db')
c = db.cursor()

create_response_iphone_table()

# Define age ranges and genders
age_ranges = ["<18", "18-25", "26-35", "36-45", ">45"]
genders = ["male", "female"]

# Define a dictionary to store age range and gender for each user
user_info = {}

# Generate age range and gender for each user
for Respondent_ID in range(1, 31):
    Age_Range = random.choice(age_ranges)
    Gender = random.choice(genders)
    user_info[Respondent_ID] = (Age_Range, Gender)

# Define function to randomly generate responses
def generate_responses():
    # One attribute should be 1, one -1, others 0
    responses = [1, -1] + [0] * 3
    random.shuffle(responses)
    return responses

# Iterate over users, blocks, and tasks to generate responses
for Respondent_ID in range(1, 31):
    # Determine the block number based on the current user
    Block = (Respondent_ID - 1) % 10 + 1
    for Task in range(1, 11):
        Age_Range, Gender = user_info[Respondent_ID]  # Get age range and gender for this user
        # Generate responses for attributes
        responses = generate_responses()
        # Retrieve attributes from survey_Apple__Iphone for the given user and block
        c.execute("SELECT block, task, item1, item2, item3, item4, item5 FROM survey_Apple__Iphone WHERE block=? AND task=?", (Block, Task,))
        attributes = c.fetchone()
        # Insert responses into response_Apple__Iphone table
        for i, Attribute in enumerate(attributes[2:]):  # Skip block and task columns
            c.execute("INSERT INTO response_Apple__Iphone (Respondent_ID, Attribute, Block, Task, Response, Age_Range, Gender) VALUES (?, ?, ?, ?, ?, ?, ?)", (Respondent_ID, Attribute, Block, Task, responses[i], Age_Range, Gender))

# Commit changes and close connection
db.commit()
db.close()


