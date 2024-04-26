import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

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
for user in range(1, 31):
    age_range = random.choice(age_ranges)
    gender = random.choice(genders)
    user_info[user] = (age_range, gender)

# Define function to randomly generate responses
def generate_responses():
    # One attribute should be 1, one -1, others 0
    responses = [1, -1] + [0] * 3
    random.shuffle(responses)
    return responses

# Iterate over users, blocks, and tasks to generate responses
for user in range(1, 31):
    # Determine the block number based on the current user
    block = (user - 1) % 10 + 1
    for task in range(1, 11):
        age_range, gender = user_info[user]  # Get age range and gender for this user
        # Generate responses for attributes
        responses = generate_responses()
        # Retrieve attributes from survey_Apple__Iphone for the given user and block
        c.execute("SELECT block, task, item1, item2, item3, item4, item5 FROM survey_Apple__Iphone WHERE block=? AND task=?", (block, task,))
        attributes = c.fetchone()
        # Insert responses into response_Apple__Iphone table
        for i, attribute in enumerate(attributes[2:]):  # Skip block and task columns
            c.execute("INSERT INTO response_Apple__Iphone (user, block, task, attribute, response, age_range, gender) VALUES (?, ?, ?, ?, ?, ?, ?)", (user, block, task, attribute, responses[i], age_range, gender))

# Commit changes and close connection
db.commit()
db.close()


