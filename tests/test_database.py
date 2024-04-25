import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from BWS.database import db_interactions
import pandas as pd

'''This file is created for making sure that all functions works correctly'''

'''Simply remove the comment sign before functions and run the code'''

'''Remove the comments signs and run the code ONE BY ONE'''

'''Add the comment sign after runnning the code'''

#creating a database
cr_db = db_interactions.create_database()

#pushing flat files (in our case master_design) ointo our databse
#db_interactions.push_flat_file_to_database("master_design.csv", "Master_Design")

#reading a table
#df = db_interactions.read_table("Master_Design")
#print(df)

#insert neccessary attributes 
#inst_attr = db_interactions.insert_attributes( 'w22', ['value', 'value2', 'value3','value4','value5','value6','value7','value8','value9','value10'] )
#print(inst_attr)

#check if they were added 
#df2 = db_interactions.get_attributes('w222')
#print(df2)

#df3 = db_interactions.read_table('Attributes')
#print(df3)

#remove_column_or_row takes two arguments(column_name, to_remove)
#if to_remove is row it will remove only it if its a column_name it will remove the entire column
#df4 = db_interactions.remove_column_or_row('w222', 'value4')

#updating a row or a column name
#write a column name, a row or column name you want to replace, and what you want to replace with
#df5 = db_interactions.update_row_or_column("w222", "value8", "value88")


#get a row from a table
#get_row = db_interactions.get_row_from_survey('Master_Design', 4005)
#print(get_row)



#insert rows into a table
#you should have uniqe rowid or it will give an error
#you should have exactly the same number of values as it is in the table columns

# dataframe1 = [
#     ['Alice', 'Bob', 'Charlie', 'ee', 'ww','New York', 'Los Angeles', 'Chicago', 'dd', 'aa','New York', 'Los Angeles', 'Chicago', 'dd', 'aa']  
# ]
# df = pd.DataFrame(dataframe1)
# inserted_rows = db_interactions.insert_rows("Master_Design", df)
# print(inserted_rows)



# Create a table for response_lyov
# cr_resp_lyov = db_interactions.create_response_lyov_table()


# Store values in response_lyov table
# user = 1
# block = 1
# task = 1
# attributes = ["attribute1", "attribute2", "attribute3"]
# best_attribute = "attribute1"
# worst_attribute = "attribute3"
# age_range = "26-35"
# gender = "male"

# store_values = db_interactions.store_response(user, block, task, attributes, best_attribute, worst_attribute, age_range, gender)



'''This part doesn't belong to this milestone and we dont need them right now, it's created for the future work'''

#currently we dont need this function
#its may be needed in the future so it needs some upgrade
#creating a table (with columns)
#cr_tb = db_interactions.create_table()


'''
def insert_survey():
    pass
i will get a dataframe
i will push it to te database

db_interactions.insertsurvey(samsung, pd.df)
#it inserts survey into our database

db_interactions.get_row_from_survey()
#it gets neccessary rows for our survey

db_interactions.insert_answer()
#it inserts answers to our database

db_interactions.get_answer(company_name)
#it gets an answer from our database

db_interactions.insert_anlysis(company_name)
#it inserts analysis to our database

#remove a column or a row from the column (Specify column name, column name (if you want to remove it entirely), or a row)
#db_interactions.delete()

#update some row or a column name
#db_interactions.update()
'''