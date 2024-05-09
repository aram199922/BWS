import os
import sys
import pandas as pd

# current_directory = os.getcwd()
# sys.path.insert(0, current_directory)
from BWS.database.db_interactions import SqlHandle


'''This file is created for making sure that all functions works correctly'''

'''Simply remove the comment sign before functions and run the code'''

'''Remove the comments signs and run the code ONE BY ONE'''

'''Add the comment sign after runnning the code'''

inst = SqlHandle()

#creating a database
#inst.create_database()

#pushing flat files (in our case master_design) ointo our databse
#inst.push_flat_file_to_database("master_design.csv", "Master_Design")

#reading a table
print(inst.read_table("Master_Design"))

#insert neccessary attributes 
#print(inst.insert_attributes( 'w222', ['value', 'value2', 'value3','value4','value5','value6','value7','value8','value9','value10'] ))

#check if they were added 
#print(inst.get_attributes('w223'))

#remove_column_or_row takes two arguments(column_name, to_remove)
#if to_remove is row it will remove only it if its a column_name it will remove the entire column
#print(inst.remove_column_or_row('w222', 'value4'))

#updating a row or a column name
#write a column name, a row or column name you want to replace, and what you want to replace with
#print(inst.update_row_or_column("w222", "value8", "value88"))


#get a row from a table
#print(inst.get_row_from_survey('Master_Design', 4005))

#insert rows into a table
#you should have uniqe rowid or it will give an error
#you should have exactly the same number of values as it is in the table columns

# dataframe1 = [
#     ['Alice', 'Bob', 'Charlie', 'ee', 'ww','New York', 'Los Angeles', 'Alice', 'Bob', 'Charlie', 'ee', 'ww','New York', 'Los Angeles', "15"]  
# ]
# df = pd.DataFrame(dataframe1)
# print(inst.insert_rows("Master_Design", df))

#Create a table for response_Apple__Iphone
#cr_resp_iphone = inst.create_response_iphone_table()


# Store values in response_Apple__Iphone table
# user = 1
# block = 1
# task = 1
# attributes = ["attribute1", "attribute2", "attribute3"]
# best_attribute = "attribute1"
# worst_attribute = "attribute3"
# age_range = "26-35"
# gender = "male"

# store_values = inst.store_response(user, block, task, attributes, best_attribute, worst_attribute, age_range, gender)