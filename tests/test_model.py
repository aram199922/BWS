import os
import sys

current_directory = os.getcwd()
sys.path.insert(0, current_directory)

from BWS.model import analysis
from BWS.database import db_interactions

# Adding attributes column
# db_interactions.insert_attributes('lyov',["ram","vam","sam","kam","lam","oam","pam","zam","pip","zip","lip"])

# Getting the specific survey
#survey_design = analysis.get_survey_design('lyov')
#print(survey_design.head())

survey_design = analysis.get_survey_design('Apple__Iphone')
print(survey_design.head())

# Pushing survey to the database with name "survey.lyov"
#analysis.push_survey_design('lyov', survey_design)

# Pushing survey to the database with name "survey_Apple__Iphone"
analysis.push_survey_design('Apple__Iphone', survey_design)

# Question ?????????
#df = db_interactions.sql_to_pandas('SELECT * from survey_lyov')
#print(df.head())

#analysis.push_analysis('Apple__Iphone') 
 
#df = db_interactions.read_table("response_Apple__Iphone") 
#print(df)