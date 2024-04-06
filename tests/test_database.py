from BWS.BWS.database import Function_Codes
import os
import pandas as pd

'''This file is created for making sure that all functions works correctly'''

'''Simply remove the comment sign before functions and run the code'''

'''Remove the comments signs and run the code ONE BY ONE'''

'''Add the comment sign after runnning the code'''


#creating a database
cr_db = Function_Codes.create_database()

#pushing flat files (in our case master_design) ointo our databse
#Function_Codes.push_flat_file_to_database("master_design.csv", "Master_Design")

#reading a table
#df = Function_Codes.read_table("Master_Design")
#print(df)

#insert neccessary attributes (specify the table)
#inst_attr = Function_Codes.insert_attributes("Master_Design", 'w221', ['value1', 'value2', 'value3','value4','value5','value6','value7','value8','value9','value10'] )
#print(inst_attr)

#check if they were added 
#df2 = Function_Codes.get_attributes('Master_Design','w221')
#print(df2)

#currently we dont need this function
#its may be needed in the future so it needs some upgrade
#creating a table (with columns)
#cr_tb = Function_Codes.create_table()

'''This part doesn't belong to this milestone and we dont need them right now, it's created for the future work'''

'''
def insert_survey():
    pass
i will get a dataframe
i will push it to te database

Function_Codes.insertsurvey(samsung, pd.df)
#it inserts survey into our database

Function_Codes.get_row_from_survey()
#it gets neccessary rows for our survey

Function_Codes.insert_answer()
#it inserts answers to our database

Function_Codes.get_answer(company_name)
#it gets an answer from our database

Function_Codes.insert_anlysis(company_name)
#it inserts analysis to our database

#remove a column or a row from the column (Specify column name, column name (if you want to remove it entirely), or a row)
#Function_Codes.delete()

#update some row or a column name
#Function_CODES.update()
'''